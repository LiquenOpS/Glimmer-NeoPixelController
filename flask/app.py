from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)

ANTHIAS_BASE_URL = "http://localhost:8000/api/v2/assets"

@app.route("/listAssets", methods=["POST"])
def list_assets():
    response = requests.get(f"{ANTHIAS_BASE_URL}/")
    return jsonify({"status": "listed", "assets": response.json()})

@app.route("/createAsset", methods=["POST"])
def create_asset():
    data = request.get_json()
    asset = json.loads(data["createAsset"])
    response = requests.post(f"{ANTHIAS_BASE_URL}/assets", json=asset)
    return jsonify({"status": "created", "response": response.text})

@app.route("/updateAssetPut", methods=["POST"])
def update_asset_put():
    data = request.get_json()
    asset = json.loads(data["updateAssetPut"])
    asset_id = asset["id"]
    response = requests.put(f"{ANTHIAS_BASE_URL}/{asset_id}", json=asset)
    return jsonify({"status": "updated (PUT)", "response": response.text})

@app.route("/updateAssetPatch", methods=["POST"])
def update_asset_patch():
    data = request.get_json()
    asset = json.loads(data["updateAssetPatch"])
    asset_id = asset["id"]
    response = requests.patch(f"{ANTHIAS_BASE_URL}/{asset_id}", json=asset)
    return jsonify({"status": "updated (PATCH)", "response": response.text})

@app.route("/deleteAsset", methods=["POST"])
def delete_asset():
    data = request.get_json()
    asset = json.loads(data["deleteAsset"])
    asset_id = asset["id"]
    response = requests.delete(f"{ANTHIAS_BASE_URL}/{asset_id}")
    return jsonify({"status": "deleted", "response": response.text})
