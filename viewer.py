from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTextEdit, QPushButton, QScrollArea
)
from database import get_all_transcripts

class TranscriptViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📚 لیست متن‌های ذخیره‌شده")
        self.setGeometry(250, 250, 700, 400)

        layout = QVBoxLayout()

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        inner = QWidget()
        inner_layout = QVBoxLayout(inner)

        transcripts = get_all_transcripts()
        if not transcripts:
            inner_layout.addWidget(QLabel("❌ هیچ متنی ثبت نشده است."))
        else:
            for i, (id, video_url, audio_url, transcript) in enumerate(transcripts, 1):
                section = QTextEdit()
                section.setReadOnly(True)
                section.setHtml(f"""
                <b>🎞 ویدیو {i}:</b><br>
                🔗 لینک ویدیو: <a href="{video_url}">{video_url}</a><br>
                🎧 لینک صوت: <a href="{audio_url}">{audio_url}</a><br><br>
                📄 متن:<br>{transcript}
                """)
                inner_layout.addWidget(section)

        scroll.setWidget(inner)
        layout.addWidget(scroll)
        self.setLayout(layout)
