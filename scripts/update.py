"""每 30 分钟由 GitHub Actions 调用：抓取微博热搜与 Google 搜索趋势，写入 data/*.json。

仅用标准库；任一数据源失败时保留旧文件（不覆盖、退出码仍为 0），
避免一次网络抖动导致站点拿到空数据。
"""
import json
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"}
WEIBO_API = "https://60s.viki.moe/v2/weibo"
GOOGLE_RSS = "https://trends.google.com/trending/rss?geo=US"
HT_NS = {"ht": "https://trends.google.com/trending/rss"}


def get_text(url: str, timeout: int = 30) -> str:
    req = Request(url, headers=UA)
    with urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", "replace")


def fetch_weibo() -> list[dict]:
    j = json.loads(get_text(WEIBO_API))
    items = []
    for it in (j.get("data") or [])[:30]:
        title = (it.get("title") or "").strip()
        if not title:
            continue
        items.append({
            "title": title,
            "hot": int(it.get("hot_value") or it.get("hot") or 0),
            "url": it.get("link") or it.get("url") or "",
        })
    return items


def fetch_google() -> list[dict]:
    root = ET.fromstring(get_text(GOOGLE_RSS))
    items = []
    for node in root.iter("item"):
        title = (node.findtext("title") or "").strip()
        if not title:
            continue
        traffic = (node.findtext("ht:approx_traffic", namespaces=HT_NS) or "").strip()
        link = (node.findtext("link") or "").strip()
        items.append({"title": title, "traffic": traffic, "url": link})
    return items[:25]


def write(name: str, items: list[dict]) -> bool:
    if not items:
        return False
    path = Path("data") / name
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"updated": datetime.now(timezone.utc).isoformat(), "items": items}
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    return True


def main() -> None:
    results = {}
    for name, fn in (("weibo.json", fetch_weibo), ("google.json", fetch_google)):
        try:
            results[name] = write(name, fn())
        except Exception as exc:  # 单源失败不影响另一源
            results[name] = f"error: {exc}"
    print(results)


if __name__ == "__main__":
    main()
