const urlbar = document.getElementById("urlbar");
const browser = document.getElementById("browser");
const go = document.getElementById("go");
const fav = document.getElementById("fav");
const historyBtn = document.getElementById("history");

function navigate(url) {
    if (!url.startsWith("http")) url = "http://" + url;
    browser.src = url;

    fetch("/add_history", {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({url: url})
    });
}

go.onclick = () => navigate(urlbar.value);
urlbar.addEventListener("keypress", e => { if (e.key === "Enter") navigate(urlbar.value); });

fav.onclick = () => {
    fetch("/toggle_favorite", {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({url: browser.src})
    });
};

historyBtn.onclick = async () => {
    const res = await fetch("/get_history");
    const data = await res.json();
    alert("履歴:\n" + data.join("\n"));
};
