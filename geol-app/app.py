from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return "Server is running 🚀"

@app.route("/collect", methods=["POST"])
def collect():
    data = request.json
    print("User Details:", data)
    return jsonify({"status": "success"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)