from flask import Flask, request, jsonify
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
import re
import json
from datetime import datetime, timedelta
import requests

app = Flask(__name__)
auth = HTTPBasicAuth()

users = {
    "username": generate_password_hash("password")
}

@auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users.get(username), password):
        return username

def parse_srt(srt_text):
    chunks = re.split(r'(\d\d:\d\d:\d\d,\d\d\d --> \d\d:\d\d:\d\d,\d\d\d)', srt_text)[1:]
    subtitles = []
    for i in range(0, len(chunks), 2):
        times, text = chunks[i], chunks[i+1].strip()
        sentences = re.split(r'(?<=\D) \d+ ', text)
        for sentence in sentences:
            sentence = re.sub(r' \d+$', '', sentence)
            if sentence:
                subtitles.append((times, sentence))
    return subtitles

def calculate_pauses(subtitles):
    format_str = "%H:%M:%S,%f"
    guidance_chunks = []
    pauses = []
    previous_end = None
    for times, text in subtitles:
        start, end = re.findall(r'(\d\d:\d\d:\d\d,\d\d\d)', times)
        start = datetime.strptime(start, format_str)
        end = datetime.strptime(end, format_str)
        if previous_end is not None:
            pause = round((start - previous_end).total_seconds())
            if pause < 3 and guidance_chunks:
                guidance_chunks[-1] += " " + text
            else:
                pauses.append(pause)
                guidance_chunks.append(text)
        else:
            guidance_chunks.append(text)
        previous_end = end
    return guidance_chunks, pauses

def download_srt_file(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        return None

@app.route('/parse_srt', methods=['POST'])
@auth.login_required
def process_srt_file():
    data = request.get_json()
    file_url = data.get('file_url')

    if not file_url:
        return jsonify({"error": "No file URL provided"}), 400

    srt_text = download_srt_file(file_url)
    if not srt_text:
        return jsonify({"error": "Failed to download the SRT file"}), 500

    subtitles = parse_srt(srt_text)
    guidance_chunks, pauses = calculate_pauses(subtitles)
    return jsonify({'guidance_chunks': guidance_chunks, 'pauses': pauses}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.getenv("PORT")))
