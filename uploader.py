import os
import requests

def upload_to_tmpfiles(filepath: str) -> str:
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"فایل پیدا نشد: {filepath}")

    url = "https://tmpfiles.org/api/v1/upload"

    with open(filepath, "rb") as f:
        files = {'file': f}
        try:
            response = requests.post(url, files=files)
            response.raise_for_status()  # بررسی کد وضعیت HTTP
        except requests.exceptions.RequestException as e:
            raise Exception(f"خطا در اتصال به tmpfiles.org: {e}")

    if response.status_code != 200:
        raise Exception(f"آپلود ناموفق بود: {response.status_code} - {response.text}")

    try:
        json_resp = response.json()
        if "data" not in json_resp or "url" not in json_resp["data"]:
            raise Exception("پاسخ نامعتبر از سرور tmpfiles")
        file_url = json_resp["data"]["url"]
        return file_url
    except ValueError as e:
        raise Exception(f"خطا در پردازش پاسخ JSON: {e}")
