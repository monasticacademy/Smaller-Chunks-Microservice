from flask import Flask, request, jsonify
from flask_httpauth import HTTPTokenAuth
from werkzeug.security import generate_password_hash, check_password_hash
import os
import re

app = Flask(__name__)
auth = HTTPTokenAuth(scheme='Bearer')

users = {
    "admin": generate_password_hash("password"),  # Never store passwords in plaintext in a real app!
}
user_tokens = {}

def timestamp_to_seconds(timestamp):
    try:
        hours, minutes, seconds = timestamp.split(',')[0].split(':')
        total_seconds = int(hours) * 3600 + int(minutes) * 60 + int(seconds)
    except ValueError:
        return None
    return total_seconds

@auth.verify_token
def verify_token(token):
    if token in user_tokens:
        return user_tokens[token]
    return None

@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    if username in users and check_password_hash(users[username], password):
        token = os.urandom(24).hex()  # Generate a secure random token
        user_tokens[token] = username
        return jsonify(token=token)
    return jsonify(error='Invalid username or password'), 401

@app.route('/convert', methods=['POST'])
@auth.login_required
def convert():
    # Rest of the code goes here...

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
