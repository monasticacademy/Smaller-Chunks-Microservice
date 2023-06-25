from flask import Flask, request, jsonify, make_response
from functools import wraps

app = Flask(__name__)

# Basic HTTP Authentication
def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

def check_auth(username, password):
    # Replace 'admin' and 'secret' with your desired username and password
    return username == 'admin' and password == 'secret'

def authenticate():
    message = {'message': "Authentication required."}
    resp = make_response(jsonify(message))
    resp.status_code = 401
    resp.headers['WWW-Authenticate'] = 'Basic realm="Example"'
    return resp

# Modify guidance function
def modify_guidance(json_input):
    guidance_chunks = json_input.get("guidance_chunks", [])
    pauses = json_input.get("pauses", [])
    new_guidance_chunks = []
    new_pauses = []
    for chunk, pause in zip(guidance_chunks, pauses):
        if len(chunk) > 250:
            sentences = chunk.split(". ")
            for i, sentence in enumerate(sentences):
                new_guidance_chunks.append(sentence)
                if i == len(sentences) - 1:
                    new_pauses.append(pause)
                else:
                    new_pauses.append(0)
        else:
            new_guidance_chunks.append(chunk)
            new_pauses.append(pause)
    json_input["guidance_chunks"] = new_guidance_chunks
    json_input["pauses"] = new_pauses
    return json_input

# API endpoint
@app.route('/modify_guidance', methods=['POST'])
@requires_auth
def api_modify_guidance():
    json_input = request.json
    result = modify_guidance(json_input)
    return jsonify(result)

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.getenv("PORT")))
