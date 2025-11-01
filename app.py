from flask import Flask, render_template, request
from search_engine import fetch_page
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

    # まずキャッシュを確認
    cached = get_cached_page(query)
    if cached:
        return render_template('result.html', title=query, content=cached, cached=True)

    # 新しいページを取得
    html = fetch_page(query)
    if not html:
        return render_template('index.html', error="ページを取得できませんでした。")

    save_page(query, html)
    return render_template('result.html', title=query, content=html, cached=False)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
