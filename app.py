from flask import Flask, request, jsonify
import json
import os
import logging
import functools
import sqlite3

# This is likely not thread safe.

CONTAINER_HOSTING_SSH_SETUP_HANDLER_API_KEY = os.getenv("CONTAINER_HOSTING_SSH_SETUP_HANDLER_API_KEY", None)
AUTHORIZED_KEYS_PATH = os.getenv("AUTHORIZED_KEYS_PATH", None)
APPS_DB_FULL_PATH = os.getenv("APPS_DB_FULL_PATH", None)

if CONTAINER_HOSTING_SSH_SETUP_HANDLER_API_KEY is None:
    exit("CONTAINER_HOSTING_SSH_SETUP_HANDLER_API_KEY must be set")

if AUTHORIZED_KEYS_PATH is None:
    exit("AUTHORIZED_KEYS_PATH must be set")

if APPS_DB_FULL_PATH is None:
    exit("APPS_DB_FULL_PATH must be set")

app = Flask(__name__)

def api_key_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        try:
            api_key = request.json['CONTAINER_HOSTING_SSH_SETUP_HANDLER_API_KEY']
            if api_key != CONTAINER_HOSTING_SSH_SETUP_HANDLER_API_KEY:
                msg = "Invalid api key sent for CONTAINER_HOSTING_SSH_SETUP_HANDLER_API_KEY"
                logging.warning(msg)
                return jsonify(msg), 401
        except Exception as e:
           msg = f"Failed authentication {e}"
           logging.error(msg)
           return jsonify("Failed authentication"), 401
        return view(**kwargs)

    return wrapped_view

@app.route("/", methods=["GET", "POST"])
@api_key_required
def index():
    payload = json.loads(request.data.decode("utf-8"))

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


@app.route("/CONTAINER_HOSTING_API_KEY", methods=["POST"])
@api_key_required
def store_CONTAINER_HOSTING_API_KEY():
    """Store users app CONTAINER_HOSTING_API_KEY
    each APP_NAME has its own CONTAINER_HOSTING_API_KEY"""
    data = request.json
    APP_NAME = data["APP_NAME"]
    CONTAINER_HOSTING_API_KEY = data["CONTAINER_HOSTING_API_KEY"]
    # Store APP_NAME and its CONTAINER_HOSTING_API_KEY
    con = sqlite3.connect(APPS_DB_FULL_PATH)
    cur = con.cursor()
    # CREATE TABLE container (container TEXT NOT NULL, CONTAINER_HOSTING_API_KEY TEXT);
    query = "INSERT INTO container (container, CONTAINER_HOSTING_API_KEY) VALUES (?, ?)"
    cur.execute(query, (APP_NAME, CONTAINER_HOSTING_API_KEY))
    con.commit()
    return CONTAINER_HOSTING_API_KEY
