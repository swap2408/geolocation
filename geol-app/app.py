from flask import Flask, request, jsonify, send_from_directory, url_for, session, redirect
from pymongo import MongoClient
from datetime import datetime
from bson.objectid import ObjectId
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
secretkey = os.getenv("secret_key")

app.secret_key = secretkey
# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")  # change if using Atlas
client = MongoClient(MONGO_URI)

db = client[DB_NAME]        # database name
collection = db[COLLECTION_NAME]      # collection name

@app.route("/")
def home():
    return send_from_directory('.', 'index.html')

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        ADMIN_USER = os.getenv("ADMIN_USER")
        ADMIN_PASS = os.getenv("ADMIN_PASS")
        if username == ADMIN_USER and password == ADMIN_PASS:
            session["user"] = username
            return redirect("/admin")
        else:
            return "Invalid credentials", 401

    return send_from_directory('.', 'login.html')
def is_logged_in():
    return "user" in session


@app.route("/admin")
def admin():
    if not is_logged_in():
        return redirect("/login")
    return send_from_directory('.', 'admin.html')


@app.route("/logs")
def get_logs():
    if not is_logged_in():
        return jsonify({"error": "unauthorized"}), 401

    logs = list(collection.find().sort("timestamp", -1))
    for log in logs:
        log["_id"] = str(log["_id"])
    return jsonify(logs)


@app.route("/delete/<id>", methods=["DELETE"])
def delete_log(id):
    if not is_logged_in():
        return jsonify({"error": "unauthorized"}), 401

    collection.delete_one({"_id": ObjectId(id)})
    return jsonify({"status": "deleted"})

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")

@app.route("/collect", methods=["POST"])
def collect():
    data = request.json

    if not data:
        return jsonify({"status": "error", "message": "No data received"}), 400

    # Add extra useful info
    data["timestamp"] = datetime.utcnow()
    forwarded_for = request.headers.get('X-Forwarded-For')

    if forwarded_for:
      
        ip = forwarded_for.split(',')[0].strip()
    else:
        ip = request.remote_addr
    data["ip"] = ip

    # Insert into MongoDB
    collection.insert_one(data)

    print("Stored User Details:", data)

    return jsonify({"status": "success"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
