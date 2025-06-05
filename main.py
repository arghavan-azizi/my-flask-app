import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QTextEdit, QMessageBox)
from PyQt5.QtCore import QTimer
import requests

SERVER_URL = "https://mood-conditions-developing-premises.trycloudflare.com"  # یا آدرس Cloudflare Tunnel

class VideoProcessorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.job_id = None
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle('پردازشگر ویدیو فارسی')
        self.setGeometry(100, 100, 800, 600)
        
        layout = QVBoxLayout()
        
        # ورودی لینک
        self.url_label = QLabel('لینک ویدیو را وارد کنید:')
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText('مثال: https://aparat.com/v/...')
        
        # دکمه پردازش
        self.process_btn = QPushButton('پردازش ویدیو')
        self.process_btn.clicked.connect(self.process_video)
        
        # نمایش نتیجه
        self.result_display = QTextEdit()
        self.result_display.setReadOnly(True)
        
        # وضعیت
        self.status_label = QLabel('وضعیت: آماده')
        
        # چیدمان
        layout.addWidget(self.url_label)
        layout.addWidget(self.url_input)
        layout.addWidget(self.process_btn)
        layout.addWidget(QLabel('نتایج:'))
        layout.addWidget(self.result_display)
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
        
    def process_video(self):
        url = self.url_input.text().strip()
        
        if not url:
            self.show_error('لطفاً لینک ویدیو را وارد کنید')
            return
            
        self.set_ui_state(processing=True)
        self.result_display.clear()
        self.status_label.setText('وضعیت: در حال ارسال درخواست...')
        
        try:
            # ارسال به سرور
            response = requests.post(
                f"{SERVER_URL}/submit",
                json={"video_url": url},
                timeout=30
            )
            
            if response.status_code == 200:
                self.job_id = response.json().get("job_id")
                self.status_label.setText('وضعیت: در حال پردازش در Kaggle...')
                self.check_status()
            else:
                self.show_error(f"خطای سرور: {response.text}")
                
        except Exception as e:
            self.show_error(f"خطا در ارتباط با سرور: {str(e)}")
    
    def check_status(self):
        try:
            response = requests.get(
                f"{SERVER_URL}/status/{self.job_id}",
                timeout=10
            )
            data = response.json()
            
            if data.get("status") == "تکمیل شده":
                self.result_display.setPlainText(data.get("transcript", ""))
                self.status_label.setText('وضعیت: پردازش کامل شد')
                self.set_ui_state(processing=False)
            elif data.get("status") == "خطا":
                self.show_error(data.get("error", "خطای ناشناخته"))
            else:
                QTimer.singleShot(5000, self.check_status)
                
        except Exception as e:
            self.show_error(f"خطا در بررسی وضعیت: {str(e)}")
    
    def set_ui_state(self, processing: bool):
        self.process_btn.setDisabled(processing)
        self.url_input.setDisabled(processing)
    
    def show_error(self, message: str):
        QMessageBox.critical(self, "خطا", message)
        self.status_label.setText(f'وضعیت: خطا - {message[:50]}...')
        self.set_ui_state(processing=False)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = VideoProcessorApp()
    window.show()
    sys.exit(app.exec_())