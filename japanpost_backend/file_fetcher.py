import os
import requests

RESOURCE_DIR = "resources"


def download_zip(url: str, save_as: str = None) -> str:
    if not os.path.exists(RESOURCE_DIR):
        os.makedirs(RESOURCE_DIR)

    filename = save_as or url.split("/")[-1]
    save_path = os.path.join(RESOURCE_DIR, filename)

    if os.path.exists(save_path):
        print(f"[INFO] すでに存在：{save_path}")
        return save_path

    print(f"[INFO] ダウンロード中: {url}")
    response = requests.get(url, timeout=30)
    response.raise_for_status()

    with open(save_path, "wb") as f:
        f.write(response.content)

    print(f"[OK] 保存完了: {save_path}")
    return save_path
