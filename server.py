from flask import Flask, request, jsonify
import uuid
import time
from threading import Lock
import logging
from queue import Queue

app = Flask(__name__)
app.logger.setLevel(logging.INFO)

# ساختارهای داده برای مدیریت کارها
jobs_lock = Lock()
JOBS = {}  # job_id -> {status, video_url, start_time, transcript}
KAGGLE_TASKS = Queue()  # صف کارها برای Kaggle

@app.route('/submit', methods=['POST'])
def submit_job():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    video_url = data.get("video_url")

    if not video_url:
        return jsonify({"error": "لینک ویدیو الزامی است"}), 400

    job_id = str(uuid.uuid4())

    with jobs_lock:
        JOBS[job_id] = {
            "status": "در انتظار پردازش",
            "video_url": video_url,
            "start_time": time.time(),
            "transcript": None
        }
        KAGGLE_TASKS.put({
            "job_id": job_id,
            "video_url": video_url
        })

    app.logger.info(f"[ثبت کار جدید] ID: {job_id}")
    return jsonify({
        "job_id": job_id,
        "status_url": f"/status/{job_id}"
    })


@app.route('/status/<job_id>', methods=['GET'])
def check_status(job_id):
    with jobs_lock:
        job = JOBS.get(job_id)

    if not job:
        return jsonify({"error": "کار مورد نظر یافت نشد"}), 404

    return jsonify({
        "status": job["status"],
        "transcript": job.get("transcript"),
        "processing_time": round(time.time() - job["start_time"], 2)
    })


@app.route('/get_kaggle_task', methods=['GET'])
def get_kaggle_task():
    if KAGGLE_TASKS.empty():
        return jsonify({"status": "no_task"}), 200

    task = KAGGLE_TASKS.get()
    app.logger.info(f"[ارسال کار به Kaggle] ID: {task['job_id']}")
    return jsonify(task)


@app.route('/update_job', methods=['POST'])
def update_job():
    if not request.is_json:
        return jsonify({"error": "درخواست باید JSON باشد"}), 400

    data = request.get_json()
    job_id = data.get("job_id")
    status = data.get("status")
    transcript = data.get("transcript", None)

    if not job_id or not status:
        return jsonify({"error": "پارامترهای ناقص"}), 400

    with jobs_lock:
        if job_id not in JOBS:
            return jsonify({"error": "کار یافت نشد"}), 404

        JOBS[job_id]["status"] = status
        if transcript:
            JOBS[job_id]["transcript"] = transcript

    app.logger.info(f"[آپدیت وضعیت کار] ID: {job_id}")
    return jsonify({"status": "success"})


@app.route('/submit_transcript', methods=['POST'])
def submit_transcript():
    if not request.is_json:
        return jsonify({"error": "درخواست باید JSON باشد"}), 400

    data = request.get_json()
    job_id = data.get("job_id")
    transcript = data.get("transcript")

    if not job_id or not transcript:
        return jsonify({"error": "پارامترهای ناقص"}), 400

    with jobs_lock:
        if job_id not in JOBS:
            return jsonify({"error": "کار یافت نشد"}), 404

        JOBS[job_id]["transcript"] = transcript
        JOBS[job_id]["status"] = "تکمیل‌شده"

    app.logger.info(f"[دریافت متن نهایی] ID: {job_id}")
    return jsonify({"status": "success"})


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5001))  # برای Railway نیاز است
    app.run(host="0.0.0.0", port=port, threaded=True)
