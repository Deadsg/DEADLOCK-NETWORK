# app.py

from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return jsonify({"message": "DEADSGOLD Flask API is running!"})

if __name__ == "__main__":
    app.run(port=5000)