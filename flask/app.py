from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)

ANTHIAS_BASE_URL = "http://localhost:8000/api/v2/assets"

NORTHBOUND_URL = "http://localhost:7896/iot/json"

def send_northbound_response(resp_data):
    print(type(resp_data))
    # api_key = data.get("k")
    # entity_id = data.get("i")
    api_key = "SignKey"
    entity_id = "ID-0002"
    # if not api_key or not entity_id:
    #     raise ValueError("Missing required parameters: 'k' or 'i'")

    headers = {'Content-Type': 'application/json'}
    params = {'k': api_key, 'i': entity_id}
    print(f"Sending northbound response to {NORTHBOUND_URL} with params {params} and data {json.dumps(resp_data, indent=4)}")
    try:
        response = requests.post(url=NORTHBOUND_URL, params=params, headers=headers, data=json.dumps(resp_data))
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error sending northbound response: {e}, {e.response.text}")
        return {"error": str(e)}

def list_assets(data):
    response = requests.get(
        f"{ANTHIAS_BASE_URL}/",
        headers={"Content-Type": "application/json"}
    )
    return response.json()

def create_asset(data):
    asset = data.get("createAsset")
    asset["skip_asset_check"] = False  #TODO
    response = requests.post(
        f"{ANTHIAS_BASE_URL}",
        json=asset,
        headers={"Content-Type": "application/json"}
    )
    return response.json()

def update_asset_put(data):
    asset = data.get("updateAssetPut")
    asset_id = asset["asset_id"]
    response = requests.put(
        f"{ANTHIAS_BASE_URL}/{asset_id}",
        json=asset,
        headers={"Content-Type": "application/json"}
    )
    return response.json()

def update_asset_patch(data):
    asset = data.get("updateAssetPatch")
    asset_id = asset["asset_id"]
    response = requests.patch(
        f"{ANTHIAS_BASE_URL}/{asset_id}",
        json=asset,
        headers={"Content-Type": "application/json"}
    )
    return response.json()

def delete_asset(data):
    asset = data.get("deleteAsset")
    asset_id = asset["asset_id"]
    response = requests.delete(
        f"{ANTHIAS_BASE_URL}/{asset_id}",
        headers={"Content-Type": "application/json"}
    )

    print(response.text)
    print(response.status_code)
    return response.json()

@app.route("/command", methods=["POST"])
def dispatch_asset_command():
    data = request.get_json()
    print(data)
    if data is not None:
        for key, value in data.items():
            if isinstance(value, dict):
                for k, v in value.items():
                    print(f"{k}: {type(v)}")
    result = {}

    if isinstance(data.get('listAssets'), dict):
        result = list_assets(data)
    elif isinstance(data.get('createAsset'), dict):
        result = create_asset(data)
    elif isinstance(data.get('updateAssetPut'), dict):
        result = update_asset_put(data)
    elif isinstance(data.get('updateAssetPatch'), dict):
        result = update_asset_patch(data)
    elif isinstance(data.get('deleteAsset'), dict):
        result = delete_asset(data)
    else:
        return jsonify({"error": "Unknown command"}), 400
    
    send_northbound_response(result)
    return jsonify(result)
