from flask import Flask, render_template, request
from whoosh.index import create_in, open_dir
from whoosh.fields import Schema, TEXT, ID
from whoosh.qparser import QueryParser
from bs4 import BeautifulSoup
import os
import requests

app = Flask(__name__)

# --- Whoosh設定 ---
INDEX_DIR = "indexdir"
if not os.path.exists(INDEX_DIR):
    os.mkdir(INDEX_DIR)
    schema = Schema(title=TEXT(stored=True), path=ID(stored=True), content=TEXT)
    ix = create_in(INDEX_DIR, schema)
else:
    ix = open_dir(INDEX_DIR)


def add_to_index(title, path, content):
    """ページをWhooshインデックスに登録"""
    writer = ix.writer()
    writer.add_document(title=title, path=path, content=content)
    writer.commit()


def fetch_page(url):
    """URLからページ内容を取得"""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        title = soup.title.string if soup.title else url
        text = soup.get_text()
        add_to_index(title, url, text)
        return title, text
    except Exception as e:
        return f"アクセス失敗: {e}", ""


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/search", methods=["GET"])
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


@app.route("/go", methods=["GET"])
def go():
    url = request.args.get("url", "")
    if not url.startswith("http"):
        url = "https://" + url
    title, text = fetch_page(url)
    return render_template("page.html", title=title, content=text)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
