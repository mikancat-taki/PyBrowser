from flask import Flask, render_template, request, jsonify
import json
import os

app = Flask(__name__)

HISTORY_FILE = "history.json"
FAVORITES_FILE = "favorites.json"

def load_json(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return json.load(f)
    return []

def save_json(file_path, data):
    with open(file_path, "w") as f:
        json.dump(data, f)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/add_history", methods=["POST"])
def add_history():
    url = request.json.get("url")
    history = load_json(HISTORY_FILE)
    if url not in history:
        history.append(url)
        save_json(HISTORY_FILE, history)
    return jsonify({"status": "ok"})

@app.route("/get_history")
def get_history():
    return jsonify(load_json(HISTORY_FILE))

@app.route("/toggle_favorite", methods=["POST"])
def toggle_favorite():
    url = request.json.get("url")
    favorites = load_json(FAVORITES_FILE)
    if url in favorites:
        favorites.remove(url)
    else:
        favorites.append(url)
    save_json(FAVORITES_FILE, favorites)
    return jsonify({"status": "ok"})

@app.route("/get_favorites")
def get_favorites():
    return jsonify(load_json(FAVORITES_FILE))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
