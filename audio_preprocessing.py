import librosa
import numpy as np
import noisereduce as nr
import soundfile as sf
from pydub import AudioSegment, silence
import os
from typing import List

def preprocess_audio(input_path: str, output_dir: str, min_silence_len: int = 500) -> List[str]:
    """نسخه بهبودیافته با پارامترهای قابل تنظیم"""
    try:
        # بارگذاری با librosa
        y, sr = librosa.load(input_path, sr=16000, mono=True)
        
        # کاهش نویز
        reduced_noise = nr.reduce_noise(
            y=y, 
            sr=sr,
            stationary=True,
            prop_decrease=0.75
        )
        
        # نرمال‌سازی
        norm_audio = reduced_noise / np.max(np.abs(reduced_noise))
        
        # ذخیره موقت
        os.makedirs(output_dir, exist_ok=True)
        temp_path = os.path.join(output_dir, "temp_normalized.wav")
        sf.write(temp_path, norm_audio, sr)
        
        # تقسیم بر اساس سکوت
        audio = AudioSegment.from_wav(temp_path)
        silence_thresh = audio.dBFS - 14
        chunks = silence.split_on_silence(
            audio,
            min_silence_len=min_silence_len,
            silence_thresh=silence_thresh,
            keep_silence=200  # حفظ 200ms سکوت بین بخش‌ها
        )
        
        # ذخیره بخش‌ها
        segments = []
        for i, chunk in enumerate(chunks):
            chunk = chunk.set_frame_rate(16000).set_channels(1)
            seg_path = os.path.join(output_dir, f"segment_{i:03d}.wav")
            chunk.export(seg_path, format="wav")
            segments.append(seg_path)
            
        return segments
        
    finally:
        # حذف فایل موقت
        if os.path.exists(temp_path):
            os.remove(temp_path)