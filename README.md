# mecha-hot-api

[MECHA-NAV](https://hengjuzhan.github.io/mecha/) 的热搜数据源仓库。GitHub Actions 每 30 分钟抓取一次并提交 JSON 到 `data/`，前端经 jsDelivr / raw 直连读取。

- `data/weibo.json` — 微博热搜（来自 [vikiboss/60s](https://github.com/vikiboss/60s) 公共 API）
- `data/google.json` — Google 搜索趋势（Google Trends 官方 RSS，geo=US）

非 fork 的独立仓库，Actions 不会被 GitHub 自动禁用；任一数据源抓取失败时保留上次数据。

前端拉取链路：jsDelivr CDN（purge 刷新）→ raw.githubusercontent.com → CORS 代理，详见 [mecha 仓库](https://github.com/hengjuzhan/mecha) `src/components/widgets/TechNewsBoard.tsx`。
