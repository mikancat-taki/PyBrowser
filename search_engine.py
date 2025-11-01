import requests
from bs4 import BeautifulSoup

def fetch_page(query):
    try:
        # キーワードをもとにDuckDuckGo HTML検索を利用（API不要）
        search_url = f"https://duckduckgo.com/html/?q={query}"
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(search_url, headers=headers, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")

        # 検索結果リンクを抽出
        results = soup.select(".result__a")
        if not results:
            return "<p>検索結果が見つかりません。</p>"

        html = "<h2>検索結果</h2><ul>"
        for r in results[:10]:
            url = r["href"]
            title = r.get_text()
            html += f'<li><a href="{url}" target="_blank">{title}</a></li>'
        html += "</ul>"
        return html
    except Exception as e:
        return f"<p>エラーが発生しました: {e}</p>"
