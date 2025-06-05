import sqlite3
import os
from typing import List, Tuple
from datetime import datetime

DB_PATH = os.path.join("data", "transcripts.db")

def get_db_connection():
    """اتصال به دیتابیس با مدیریت خودکار"""
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # دسترسی به ستون‌ها با نام
    return conn

def init_db():
    """ایجاد جدول با ساختار بهبودیافته"""
    with get_db_connection() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS transcripts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id TEXT UNIQUE,
            video_url TEXT NOT NULL,
            audio_url TEXT,
            transcript TEXT,
            processing_time REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_job_id ON transcripts(job_id)")

def insert_transcript(job_id: str, video_url: str, audio_url: str, transcript_text: str, processing_time: float = None):
    """درج با مدیریت کامل خطاها"""
    try:
        with get_db_connection() as conn:
            conn.execute("""
            INSERT INTO transcripts (job_id, video_url, audio_url, transcript, processing_time)
            VALUES (?, ?, ?, ?, ?)
            """, (job_id, video_url, audio_url, transcript_text, processing_time))
    except sqlite3.IntegrityError:
        raise ValueError(f"Job ID {job_id} already exists")

def get_all_transcripts() -> List[Tuple]:
    """دریافت تمام رکوردها با مرتب‌سازی"""
    with get_db_connection() as conn:
        cursor = conn.execute("""
        SELECT id, job_id, video_url, audio_url, 
               substr(transcript, 1, 100) || '...' as preview,
               processing_time, 
               datetime(created_at, 'localtime') as created_at
        FROM transcripts 
        ORDER BY created_at DESC
        """)
        return cursor.fetchall()

# تست
if __name__ == "__main__":
    init_db()
    try:
        insert_transcript(
            job_id="test123",
            video_url="https://example.com/video1",
            audio_url="https://example.com/audio1.wav",
            transcript_text="این یک متن تستی است",
            processing_time=12.5
        )
        print(get_all_transcripts())
    except Exception as e:
        print(f"Error: {e}")