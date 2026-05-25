# bluetti-ericdy

Cloudflare Worker：图片 `PUT` 上传到 R2，返回公网 URL（与 `my-image-uploader` 接口兼容）。

## 当前阶段

| 组件 | 状态 |
|------|------|
| Worker 代码 (`src/index.ts`) | 已实现，**未绑 R2 时 PUT 返回 503 说明** |
| 影刀 / Python 客户端 (`rpa/`) | 已配置联调 URL，可直接调用 |
| 自有 R2 | 申请后在 `wrangler.toml` 取消注释并部署 |

联调 Worker（非本账号，请少测）：`https://my-image-uploader.carolyn-700.workers.dev`

## 接口约定

- `PUT /{filename}` — body 为图片二进制，`Content-Type: application/octet-stream`
- 成功：`200` + `{"message":"上传成功!","url":"https://pub-....r2.dev/..."}`
- 非 PUT：`405` + `只允许 PUT 方法上传`

## 影刀 / xbot 使用

1. 将 `rpa/upload_image.py`、`rpa/config.py` 复制到你的流程模块目录，或在本仓库调用。
2. `rpa/config.py` 中 `WORKER_URL` 已指向联调地址；自有 Worker 就绪后改为你自己的 `workers.dev` URL。
3. 流程中调用：

```python
from rpa.upload_image import upload_image_to_cf

url = upload_image_to_cf(r"D:\桌面\销售数据截图.png")
```

## 最小联调（仅 8 字节探测，避免大文件）

```bash
pip install -r requirements-rpa.txt
python scripts/test_external_worker_once.py
```

## Worker 本地开发 / 部署

```bash
npm install
npm run dev          # 未配 R2 时 PUT 会 503
npm run deploy
```

### 申请 R2 后

1. Cloudflare 控制台创建 bucket，开启公网访问（得到 `https://pub-xxxx.r2.dev` 前缀）。
2. 编辑 `wrangler.toml`，取消 `[[r2_buckets]]` 与 `[vars]` 注释并填写。
3. 将 `rpa/config.py` 的 `WORKER_URL` 改为 `https://bluett-ericdy.<子域>.workers.dev`。
4. 重新 `npm run deploy`。

## Cloudflare CI

| 配置项 | 推荐值 |
|--------|--------|
| Build command | `npm ci` |
| Deploy command | `npx wrangler deploy` |

## 路由

- `GET /health` — 是否已配置 R2 / 公网前缀
- `GET /` — `405`，提示仅支持 PUT
- `PUT /{key}` — 上传并返回 JSON
