import os
import requests
import concurrent.futures
from typing import List
from audio_extractor import download_and_extract_audio
from audio_preprocessing import preprocess_audio
import logging

def upload_to_tmpfiles(file_path: str, max_retries: int = 3) -> str:
    """آپلود با قابلیت تکرار و مدیریت خطا"""
    for attempt in range(max_retries):
        try:
            with open(file_path, 'rb') as f:
                response = requests.post(
                    'https://tmpfiles.org/api/v1/upload',
                    files={'file': f},
                    timeout=30
                )
            response.raise_for_status()
            return response.json()['data']['url']
        except Exception as e:
            if attempt == max_retries - 1:
                logging.error(f"Failed to upload {file_path} after {max_retries} attempts")
                raise
            logging.warning(f"Upload attempt {attempt + 1} failed, retrying...")

def prepare_audio_for_kaggle(video_url: str, temp_dir: str) -> List[str]:
    """پردازش موازی برای آپلود بخش‌ها"""
    try:
        # استخراج صوت
        audio_path = download_and_extract_audio(video_url, temp_dir)
        
        # پیش‌پردازش
        segments = preprocess_audio(audio_path, temp_dir)
        
        # آپلود موازی
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(upload_to_tmpfiles, seg) for seg in segments]
            upload_links = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        return upload_links
        
    finally:
        # تمیزکاری فایل‌های موقت
        for f in os.listdir(temp_dir):
            if f.endswith('.wav'):
                os.remove(os.path.join(temp_dir, f))