from flask import Flask, render_template, request
from search_engine import fetch_page, fetch_url
from database import save_page, get_cached_page

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '').strip()
    if not query:
        return render_template('index.html', error="検索ワードを入力してください。")

    cached = get_cached_page(query)
    if cached:
        return render_template('result.html', title=query, content=cached, cached=True)

    html = fetch_page(query)
    if not html:
        return render_template('index.html', error="検索結果が見つかりませんでした。")

    save_page(query, html)
    return render_template('result.html', title=query, content=html, cached=False)

@app.route('/view')
def view():
    url = request.args.get('url', '').strip()
    if not url:
        return render_template('index.html', error="URLを入力してください。")

    html = fetch_url(url)
    if not html:
        return render_template('index.html', error="URLにアクセスできませんでした。")

    return render_template('result.html', title=url, content=html, cached=False)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
