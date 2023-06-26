from flask import Flask, request, jsonify, make_response
from functools import wraps

app = Flask(__name__)

# Function for Basic Authentication
def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

# Check if username and password match
def check_auth(username, password):
    # You can set your own username and password here
    return username == 'user' and password == 'pass'

# 401 response for incorrect credentials
def authenticate():
    message = {'message': "Authentication required."}
    resp = make_response(jsonify(message))
    resp.status_code = 401
    resp.headers['WWW-Authenticate'] = 'Basic realm="Login Required"'
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
                if i < len(sentences) - 1:
                    sentence += "."
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

# Route to modify guidance
@app.route('/modify_guidance', methods=['POST'])
@requires_auth
def modify_guidance_route():
    json_input = request.json
    return jsonify(modify_guidance(json_input))

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.getenv("PORT")))
