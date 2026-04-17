from flask import Flask, request, jsonify, send_from_directory
from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

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
