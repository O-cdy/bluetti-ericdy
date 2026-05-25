"""
影刀 / xbot 可「调用模块」使用；也可直接 python -m rpa.upload_image 做最小测试。

依赖: pip install requests
"""

from __future__ import annotations

import os
import uuid

import requests

from rpa.config import WORKER_URL


def upload_image_to_cf(local_image_path: str, worker_url: str | None = None) -> str:
    """
    上传本地图片到 Cloudflare Worker（后端写入 R2），返回公网 URL。

    :param local_image_path: 本地图片完整路径
    :param worker_url: 可选，覆盖 config.WORKER_URL
    :return: 图片公网 URL
    """
    base = (worker_url or WORKER_URL).rstrip("/")
    if not base:
        raise ValueError("WORKER_URL 未配置")

    if not os.path.exists(local_image_path):
        raise FileNotFoundError(f"错误：文件不存在 -> {local_image_path}")

    file_extension = os.path.splitext(local_image_path)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    upload_url = f"{base}/{unique_filename}"

    print(f"准备上传到: {upload_url}")

    try:
        with open(local_image_path, "rb") as f:
            image_data = f.read()

        headers = {"Content-Type": "application/octet-stream"}
        response = requests.put(upload_url, data=image_data, headers=headers, timeout=30)
        response.raise_for_status()
        result = response.json()

        if response.status_code == 200 and result.get("url"):
            print("上传成功!")
            return result["url"]

        raise ValueError(f"服务器返回异常: {result.get('message', result)}")

    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"网络错误: {e}") from e
    except Exception as e:
        raise RuntimeError(f"上传过程中发生未知错误: {e}") from e


def main(args=None):
    """xbot 独立运行入口；args 可传入 {"image_path": "..."} """
    final_url = None
    try:
        image_path = None
        if isinstance(args, dict):
            image_path = args.get("image_path")
        if not image_path:
            image_path = os.environ.get("CF_TEST_IMAGE_PATH")

        if not image_path:
            raise ValueError(
                '请设置图片路径：main({"image_path": r"D:\\path\\to\\image.png"}) '
                "或环境变量 CF_TEST_IMAGE_PATH"
            )

        final_url = upload_image_to_cf(image_path)
        print("\n成功获取 Cloudflare 在线图片 URL:")
        print(final_url)
        print(f"\n钉钉 Markdown 格式:\n![图片描述]({final_url})")
    except Exception as e:
        print(f"\n操作失败: {e}")
        raise

    return final_url


if __name__ == "__main__":
    main()
