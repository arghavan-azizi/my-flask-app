import os
import yt_dlp
import ffmpeg
from typing import Optional
from datetime import datetime

def validate_video_url(url: str) -> bool:
    """اعتبارسنجی لینک ویدیو"""
    domains = ['youtube.com', 'youtu.be', 'aparat.com', 'namasha.com']
    return any(domain in url for domain in domains)

def download_and_extract_audio(video_url: str, output_dir: str) -> str:
    """نسخه بهبودیافته با مدیریت خطا و اعتبارسنجی"""
    if not validate_video_url(video_url):
        raise ValueError("لینک ویدیو نامعتبر است")

    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    audio_output = os.path.join(output_dir, f'audio_{timestamp}.wav')

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(output_dir, 'temp_video.%(ext)s'),
        'quiet': True,
        'nocheckcertificate': True,
        'extract_audio': True,
        'audio_format': 'wav',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192',
        }],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            temp_path = ydl.prepare_filename(info)
        
        # تبدیل به 16kHz تک کاناله
        (
            ffmpeg.input(temp_path)
            .output(audio_output, ac=1, ar=16000)
            .overwrite_output()
            .run(cmd='ffmpeg', capture_stdout=True, capture_stderr=True)
        )
        
        # حذف فایل موقت
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
        return audio_output

    except Exception as e:
        # تمیزکاری فایل‌های موقت در صورت خطا
        for f in os.listdir(output_dir):
            if f.startswith('temp_video'):
                os.remove(os.path.join(output_dir, f))
        raise RuntimeError(f"خطا در پردازش ویدیو: {str(e)}")