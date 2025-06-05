import requests

job_id = "از فایل job_id.txt بخوان یا دستی بنویس"
with open("transcript_final.txt", "r", encoding="utf-8") as f:
    transcript = f.read()

response = requests.post("http://127.0.0.1:5001/submit_transcript", json={
    "job_id": job_id,
    "transcript": transcript
})

print(response.json())
