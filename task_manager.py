import json
import os
import requests

def create_task_file(audio_url: str, output="task.json") -> str:
    """
    یک فایل JSON حاوی لینک صوتی می‌سازد
    """
    task = {"audio_url": audio_url}
    with open(output, "w", encoding="utf-8") as f:
        json.dump(task, f, ensure_ascii=False, indent=2)
    return output

def upload_task_file(task_file: str) -> str:
    """
    فایل JSON ساخته شده را در tmpfiles.org آپلود می‌کند و لینک دانلود مستقیم می‌دهد
    """
    if not os.path.exists(task_file):
        raise FileNotFoundError(f"فایل پیدا نشد: {task_file}")

    url = "https://tmpfiles.org/api/v1/upload"
    with open(task_file, "rb") as f:
        files = {'file': f}
        response = requests.post(url, files=files)
        response.raise_for_status()

    json_resp = response.json()
    # لینک مستقیم فایل JSON آپلود شده
    return json_resp["data"]["url"]
