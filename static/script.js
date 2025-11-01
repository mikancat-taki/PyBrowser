// タブ管理用構造（簡易）
const tabs = [];
let currentTabIndex = 0;

function createNewTab(url = "about:blank") {
  const tab = {
    iframe: document.createElement("iframe"),
    url: url
  };
  tab.iframe.src = url;
  tab.iframe.style.display = "none"; // 最初は隠す
  document.body.appendChild(tab.iframe); // または専用コンテナへ
  tabs.push(tab);
  switchToTab(tabs.length - 1);
}

function switchToTab(index) {
  if (index < 0 || index >= tabs.length) return;
  // hide current
  tabs[currentTabIndex].iframe.style.display = "none";
  // show new
  currentTabIndex = index;
  tabs[currentTabIndex].iframe.style.display = "block";
  // update URL bar
  document.getElementById("q").value = tabs[currentTabIndex].url;
}

function closeTab(index) {
  if (tabs.length <= 1) return;
  const tab = tabs[index];
  tab.iframe.remove();
  tabs.splice(index, 1);
  if (currentTabIndex >= tabs.length) currentTabIndex = tabs.length -1;
  switchToTab(currentTabIndex);
}

// ショートカットキー実装
document.addEventListener("keydown", (e) => {
  if (e.ctrlKey && e.key === "t") { // Ctrl+T 新タブ
    createNewTab("https://www.google.com");
    e.preventDefault();
  } else if (e.ctrlKey && e.key === "w") { // Ctrl+W 閉じる
    closeTab(currentTabIndex);
    e.preventDefault();
  }
});

// テーマ切替
let darkMode = true;
function toggleTheme() {
  darkMode = !darkMode;
  document.body.classList.toggle("dark-mode", darkMode);
}
document.getElementById("themeToggleBtn").onclick = toggleTheme;
