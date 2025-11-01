import os
import sqlite3
from flask import Flask, render_template, request
from whoosh.index import create_in, open_dir
from whoosh.fields import Schema, TEXT, ID
from whoosh.qparser import QueryParser
from bs4 import BeautifulSoup
import requests

app = Flask(__name__)

# === ディレクトリ設定 ===
INDEX_DIR = "indexdir"
DB_PATH = "cache.db"

# === Whooshインデックス作成 ===
if not os.path.exists(INDEX_DIR):
    os.mkdir(INDEX_DIR)
    schema = Schema(title=TEXT(stored=True), path=ID(stored=True), content=TEXT)
    create_in(INDEX_DIR, schema)
ix = open_dir(INDEX_DIR)

# === SQLite初期化 ===
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS cache (
            url TEXT PRIMARY KEY,
            title TEXT,
            content TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()


def cache_get(url):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT title, content FROM cache WHERE url=?", (url,))
    row = c.fetchone()
    conn.close()
    return row if row else None


def cache_set(url, title, content):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("REPLACE INTO cache (url, title, content) VALUES (?, ?, ?)", (url, title, content))
    conn.commit()
    conn.close()


def add_to_index(title, path, content):
    """ページをWhooshに追加"""
    writer = ix.writer()
    writer.add_document(title=title, path=path, content=content)
    writer.commit()


def fetch_page(url):
    """ページ取得＋キャッシュ"""
    cached = cache_get(url)
    if cached:
        return cached[0], cached[1]

    try:
        if not url.startswith("http"):
            url = "https://" + url
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        title = soup.title.string if soup.title else url
        text = soup.get_text()
        add_to_index(title, url, text)
        cache_set(url, title, text)
        return title, text
    except Exception as e:
        return f"アクセス失敗: {e}", ""


# === Flaskルート ===
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/search")
def search():
    query = request.args.get("q", "")
    results = []
    if query:
        with ix.searcher() as searcher:
            parser = QueryParser("content", ix.schema)
            q = parser.parse(query)
            hits = searcher.search(q, limit=10)
            results = [(hit["title"], hit["path"]) for hit in hits]
    return render_template("results.html", query=query, results=results)


@app.route("/go")
def go():
    url = request.args.get("url", "")
    title, text = fetch_page(url)
    return render_template("page.html", title=title, content=text)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
