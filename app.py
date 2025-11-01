import os
import json
import time
from urllib.parse import urljoin, urlparse
import urllib.robotparser as robotparser

import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, request, jsonify

from whoosh import index
from whoosh.fields import Schema, TEXT, ID, STORED
from whoosh.qparser import MultifieldParser

# --- 設定 ---
INDEX_DIR = "indexdir"
HISTORY_FILE = "history.json"
FAVORITES_FILE = "favorites.json"
CRAWL_MAX_PAGES = 200
CRAWL_TIMEOUT = 5  # 秒

# --- Whoosh スキーマ ---
schema = Schema(
    url=ID(stored=True, unique=True),
    title=TEXT(stored=True),
    content=TEXT
)

# --- Flask ---
app = Flask(__name__, static_folder="static", template_folder="templates")

# --- ユーティリティ: JSON読み書き ---
def load_json(path, default=None):
    if default is None:
        default = []
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default
    return default

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# --- インデックス初期化 ---
def ensure_index():
    if not os.path.exists(INDEX_DIR):
        os.makedirs(INDEX_DIR)
    if index.exists_in(INDEX_DIR):
        return index.open_dir(INDEX_DIR)
    else:
        return index.create_in(INDEX_DIR, schema)

ix = ensure_index()

# --- robots.txt チェック ---
def can_fetch(url, user_agent="*"):
    parsed = urlparse(url)
    base = f"{parsed.scheme}://{parsed.netloc}"
    rp = robotparser.RobotFileParser()
    rp.set_url(urljoin(base, "/robots.txt"))
    try:
        rp.read()
    except Exception:
        # robots.txt が取得できない場合は保守的に許可する（必要ならここ変更）
        return True
    return rp.can_fetch(user_agent, url)

# --- ページ取得 & 正規化/抽出 ---
def fetch_and_parse(url):
    try:
        r = requests.get(url, timeout=CRAWL_TIMEOUT, headers={"User-Agent":"PySelfSearchBot/1.0"})
        if r.status_code != 200 or "text/html" not in r.headers.get("Content-Type",""):
            return None
        soup = BeautifulSoup(r.text, "html.parser")
        title = soup.title.string.strip() if soup.title and soup.title.string else url
        # 本文テキストを簡易抽出（スクリプト/スタイルは除去）
        for s in soup(["script", "style", "noscript"]):
            s.decompose()
        text = soup.get_text(separator="\n")
        text = "\n".join([line.strip() for line in text.splitlines() if line.strip()])
        # 収集するリンク
        links = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            joined = urljoin(url, href)
            # 正規化：スキームを保持するリンクのみ
            if urlparse(joined).scheme in ("http", "https"):
                links.append(joined)
        return {"url": url, "title": title, "content": text, "links": links}
    except Exception:
        return None

# --- インデックスへ追加/更新 ---
def index_document(doc):
    global ix
    writer = ix.writer()
    try:
        writer.update_document(url=doc["url"], title=doc["title"], content=doc["content"])
        writer.commit()
        return True
    except Exception as e:
        try:
            writer.cancel()
        except:
            pass
        return False

# --- シンプルなBFSクロール ---
def crawl(seed_urls, max_pages=CRAWL_MAX_PAGES):
    seen = set()
    queue = list(seed_urls)
    count = 0
    while queue and count < max_pages:
        url = queue.pop(0)
        if url in seen:
            continue
        seen.add(url)
        # robots.txt チェック
        if not can_fetch(url):
            continue
        doc = fetch_and_parse(url)
        if not doc:
            continue
        index_document(doc)
        count += 1
        # enqueueリンク（簡易：同ドメイン優先）
        for link in doc["links"]:
            if link not in seen and len(queue) < max_pages*2:
                queue.append(link)
    return {"indexed": count, "seen": len(seen)}

# --- Flask ルート --- 
@app.route("/")
def index_route():
    return render_template("index.html")

@app.route("/search")
def search_route():
    q = request.args.get("q", "").strip()
    page = int(request.args.get("page", "1"))
    per_page = 10
    results = []
    total = 0
    if q:
        with ix.searcher() as searcher:
            parser = MultifieldParser(["title", "content"], schema=ix.schema)
            query = parser.parse(q)
            hits = searcher.search_page(query, page, pagelen=per_page, terms=True)
            total = hits.total if hasattr(hits, "total") else len(hits)
            for h in hits:
                results.append({"url": h["url"], "title": h.get("title",""), "snippet": h.highlights("content", top=2)})
    return jsonify({"q": q, "total": total, "page": page, "per_page": per_page, "results": results})

@app.route("/crawl", methods=["POST"])
def crawl_route():
    body = request.json or {}
    seeds = body.get("seeds", [])
    max_pages = int(body.get("max_pages", CRAWL_MAX_PAGES))
    if not seeds:
        return jsonify({"error":"no seeds provided"}), 400
    start = time.time()
    stats = crawl(seeds, max_pages=max_pages)
    elapsed = time.time() - start
    return jsonify({"status":"ok", "stats": stats, "elapsed": elapsed})

# 履歴 / お気に入り
@app.route("/add_history", methods=["POST"])
def add_history():
    url = (request.json or {}).get("url")
    if not url:
        return jsonify({"error":"no url"}), 400
    hist = load_json(HISTORY_FILE, [])
    if url not in hist:
        hist.append(url)
        save_json(HISTORY_FILE, hist)
    return jsonify({"status":"ok"})

@app.route("/get_history")
def get_history():
    return jsonify(load_json(HISTORY_FILE, []))

@app.route("/toggle_favorite", methods=["POST"])
def toggle_favorite():
    url = (request.json or {}).get("url")
    if not url:
        return jsonify({"error":"no url"}), 400
    fav = load_json(FAVORITES_FILE, [])
    if url in fav:
        fav.remove(url)
    else:
        fav.append(url)
    save_json(FAVORITES_FILE, fav)
    return jsonify({"status":"ok", "favorites": fav})

@app.route("/get_favorites")
def get_favorites():
    return jsonify(load_json(FAVORITES_FILE, []))

# --- app run (gunicorn で起動するのでここはデバッグ用) ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
