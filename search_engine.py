import requests
from bs4 import BeautifulSoup

def fetch_page(query):
    """DuckDuckGoのHTML検索を利用（API不要）"""
    try:
        search_url = f"https://duckduckgo.com/html/?q={query}"
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(search_url, headers=headers, timeout=10)
        res.raise_for_status()

        soup = BeautifulSoup(res.text, "html.parser")
        results = soup.select(".result__a")

        if not results:
            return "<p>検索結果が見つかりません。</p>"

        html = "<h2>🔍 検索結果</h2><ul>"
        for r in results[:10]:
            url = r["href"]
            title = r.get_text()
            html += f'<li><a href="/view?url={url}" target="_blank">{title}</a></li>'
        html += "</ul>"
        return html

    except Exception as e:
        return f"<p>エラーが発生しました: {e}</p>"

def fetch_url(url):
    """URL直接アクセス"""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        return f"<pre>{res.text}</pre>"
    except Exception as e:
        return f"<p>アクセスエラー: {e}</p>"
