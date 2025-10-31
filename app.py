from flask import Flask, request, jsonify
import json
import os
import logging
import functools
import sqlite3
import subprocess

PYTHON_LOG_LEVEL = os.getenv("PYTHON_LOG_LEVEL", "DEBUG")
log = (
    logging.getLogger()
)
handler = logging.StreamHandler()
formatter = logging.Formatter(
    "%(asctime)s %(name)-12s %(levelname)-8s %(message)s %(funcName)s %(pathname)s:%(lineno)d"
)  # noqa

# https://docs.python.org/3/library/logging.html#logging.Handler
handler.setFormatter(formatter)
handler.setLevel(
    PYTHON_LOG_LEVEL
)  # Both loggers and handlers have a setLevel method  noqa
log.addHandler(handler)

log.setLevel(PYTHON_LOG_LEVEL)


# This is likely not thread safe.

CONTAINER_HOSTING_SSH_SETUP_HANDLER_API_KEY = os.getenv("CONTAINER_HOSTING_SSH_SETUP_HANDLER_API_KEY", None)
AUTHORIZED_KEYS_PATH = os.getenv("AUTHORIZED_KEYS_PATH", None)
APPS_DB_FULL_PATH = os.getenv("APPS_DB_FULL_PATH", None)
KEY_VALUE_STORE_DB_FULL_PATTH = os.getenv("KEY_VALUE_STORE_DB_FULL_PATTH", None)

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
    con = sqlite3.connect(APPS_DB_FULL_PATH)
    cur = con.cursor()
    # CREATE TABLE container (container TEXT NOT NULL, CONTAINER_HOSTING_API_KEY TEXT);
    settings = {"APP_NAME": APP_NAME}
    query = "INSERT INTO container (container, CONTAINER_HOSTING_API_KEY) VALUES (?, ?)"
    cur.execute(query, (json.dumps(settings), CONTAINER_HOSTING_API_KEY))
    con.commit()
    return "CONTAINER_HOSTING_API_KEY has been stored"


@app.route("/STORE-KEY-VALUE", methods=["POST"])
@api_key_required
def store_KEY_VALUE():
    """
    Store KEY VALYE in key_value_store.

    Naming convention for key is: "APPNAME:KEY_NAME"
    
    e.g. myap:AMBER_SECRET, secret1234

    Store users app AMBER_SECRET 
    each APP_NAME has its own AMBER_SECRET which is
    shared with the app owner so that secrets may be stored
    securely, but also managed decoupled from a specific CI system

    TODO derive key name (app name) from API key
    """
    data = request.json
    APP_NAME = data["APP_NAME"]
    key = data["KEY"]
    value = data["VALUE"]
    con = sqlite3.connect(KEY_VALUE_STORE_DB_FULL_PATTH)
    cur = con.cursor()
    query = "INSERT INTO key_value_store (key, value) VALUES (?, ?)"
    cur.execute(query, (key, value))
    con.commit()
    return f"{key} has been stored"

