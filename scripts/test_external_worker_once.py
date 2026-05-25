"""
对外部 Worker 做一次最小 PUT 联调（约 8 字节 PNG 头），避免反复上传大文件。
运行: python scripts/test_external_worker_once.py
"""

import sys
import tempfile
import uuid
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rpa.config import WORKER_URL

# 最小合法 PNG 文件头（非完整图片，仅用于探测接口；外部 Worker 仍接受）
MINIMAL_PNG = bytes([0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A])


def main() -> int:
    name = f"probe-{uuid.uuid4().hex[:8]}.png"
    url = f"{WORKER_URL.rstrip('/')}/{name}"
    print(f"PUT {url} (payload {len(MINIMAL_PNG)} bytes)")

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        tmp.write(MINIMAL_PNG)
        path = tmp.name

    try:
        with open(path, "rb") as f:
            resp = requests.put(
                url,
                data=f.read(),
                headers={"Content-Type": "application/octet-stream"},
                timeout=30,
            )
        print(f"HTTP {resp.status_code}")
        print(resp.text)
        resp.raise_for_status()
        data = resp.json()
        if not data.get("url"):
            print("FAIL: 响应缺少 url 字段")
            return 1
        print("OK:", data["url"])
        return 0
    finally:
        Path(path).unlink(missing_ok=True)


if __name__ == "__main__":
    raise SystemExit(main())
