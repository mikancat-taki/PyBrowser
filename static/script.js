async function api(path, opts) {
  const res = await fetch(path, opts);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

const qInput = document.getElementById("q");
const searchBtn = document.getElementById("searchBtn");
const resultsDiv = document.getElementById("results");
const seedInput = document.getElementById("seedInput");
const maxPages = document.getElementById("maxPages");
const crawlBtn = document.getElementById("crawlBtn");
const crawlStatus = document.getElementById("crawlStatus");
const showFav = document.getElementById("showFav");
const showHist = document.getElementById("showHist");

function renderResults(json) {
  resultsDiv.innerHTML = `<h3>検索： ${json.q} （${json.total} 件）</h3>`;
  if (!json.results || json.results.length === 0) {
    resultsDiv.innerHTML += "<p>結果はありません</p>";
    return;
  }
  for (const r of json.results) {
    const el = document.createElement("div");
    el.className = "result";
    el.innerHTML = `<a href="${r.url}" target="_blank">${r.title}</a><div class="snippet">${r.snippet || ""}</div>`;
    resultsDiv.appendChild(el);
  }
}

searchBtn.onclick = async () => {
  const q = qInput.value.trim();
  if (!q) return;
  try {
    const res = await api(`/search?q=${encodeURIComponent(q)}`);
    // 履歴追加
    await api("/add_history", {method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify({url: location.href + "#q=" + encodeURIComponent(q)})});
    renderResults(res);
  } catch (e) {
    resultsDiv.textContent = "検索中にエラー: " + e;
  }
};

crawlBtn.onclick = async () => {
  const seedsRaw = seedInput.value.trim();
  if (!seedsRaw) { alert("シードを入力してください"); return; }
  const seeds = seedsRaw.split(",").map(s => s.trim()).filter(Boolean);
  const max_p = parseInt(maxPages.value) || 100;
  crawlStatus.textContent = "クロール中...";
  try {
    const res = await api("/crawl", {
      method:"POST",
      headers:{"Content-Type":"application/json"},
      body: JSON.stringify({seeds: seeds, max_pages: max_p})
    });
    crawlStatus.textContent = `クロール完了 - indexed: ${res.stats.indexed}, seen: ${res.stats.seen} ( ${res.elapsed.toFixed(2)}s )`;
  } catch (e) {
    crawlStatus.textContent = "クロールエラー: " + e;
  }
};

showFav.onclick = async () => {
  const favs = await api("/get_favorites");
  alert("お気に入り:\n" + (favs.length ? favs.join("\n") : "(なし)"));
};

showHist.onclick = async () => {
  const hist = await api("/get_history");
  alert("履歴:\n" + (hist.length ? hist.join("\n") : "(なし)"));
};
