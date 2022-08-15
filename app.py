from flask import Flask, request, jsonify
import json
import os
import logging

# This is likely not thread safe.

CONTAINER_HOSTING_SSH_SETUP_HANDLER_API_KEY = os.getenv("CONTAINER_HOSTING_SSH_SETUP_HANDLER_API_KEY", None)
AUTHORIZED_KEYS_PATH = os.getenv("AUTHORIZED_KEYS_PATH", None)

if CONTAINER_HOSTING_SSH_SETUP_HANDLER_API_KEY is None:
    exit("CONTAINER_HOSTING_SSH_SETUP_HANDLER_API_KEY must be set")

if AUTHORIZED_KEYS_PATH is None:
    exit("AUTHORIZED_KEYS_PATH must be set")

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    payload = json.loads(request.data.decode("utf-8"))
    api_key = payload['CONTAINER_HOSTING_SSH_SETUP_HANDLER_API_KEY']
    if api_key != CONTAINER_HOSTING_SSH_SETUP_HANDLER_API_KEY:
        msg = "Invalid api key sent for CONTAINER_HOSTING_SSH_SETUP_HANDLER_API_KEY"
        logging.warning(msg)
        return jsonify(msg), 401

    public_key = payload['public_key']
    # Append write public_key to authorized_keys
    try:
        with open(AUTHORIZED_KEYS_PATH, "a") as fp:
            fp.write(f"\n{public_key}")
            print(f"Appended public_key {public_key}")
        logging.info(public_key)
        return jsonify("Thanks- got the public_key, and appended it to authorized_keys, probably!"), 200
    except FileNotFoundError:
        logging.error(f"FileNotFoundError for {AUTHORIZED_KEYS_PATH}")
        return jsonify("Unable to append key. See logs"), 500
    except Exception as e:
        logging.error(f"Unhandled exception: {e}")
        return jsonify("Unable to append key. See logs"), 500
