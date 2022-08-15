from flask import Flask, request
import json

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    public_key = json.loads(request.data.decode("utf-8"))['public_key']
    # Append write public_key to authorized_keys
    with open("/home/dokku/.ssh/authorized_keys", "a") as fp:
        fp.write(f"\n{public_key}")
        print(f"Appended public_key {public_key}")
    print(public_key)
    print(request)
    return "Thanks- got the public_key, and appended it to authorized_keys, probably!"
