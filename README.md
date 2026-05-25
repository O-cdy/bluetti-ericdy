# bluetti-ericdy

Cloudflare Worker（方案 C）：无静态资源目录，通过 `wrangler.toml` 指定 Worker 入口部署。

## 本地开发

```bash
npm install
npm run dev
```

访问 `http://127.0.0.1:8787/` 与 `http://127.0.0.1:8787/health`。

## 部署

```bash
npm run deploy
```

## Cloudflare 控制台（Workers & Pages）

| 配置项 | 推荐值 |
|--------|--------|
| Build command | `npm ci`（可选，用于缓存依赖；也可保持 `None`） |
| Deploy command | `npx wrangler deploy` |
| Root directory | `/` |

确保 Git 仓库已包含 `wrangler.toml` 与 `src/index.ts`，且 Worker 名称 `bluett-ericdy` 与 Cloudflare 项目名称一致。

## 路由

- `GET /` — 文本探活
- `GET /health` — JSON 健康检查
