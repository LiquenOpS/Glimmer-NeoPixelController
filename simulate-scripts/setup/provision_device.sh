#!/bin/bash

if [ -z "$DEVICE_ID" ] || [ -z "$DEVICE_NAME" ]; then
  echo "Error: DEVICE_ID or DEVICE_NAME not set."
  exit 1
fi

echo "Provisioning IoT Agent with a Device...: ${DEVICE_ID} ${DEVICE_NAME}"
echo "----------------------------------------------"

PAYLOAD=$(cat <<EOF
{
    "devices": [
        {
            "device_id": "${DEVICE_ID}",
            "entity_name": "${DEVICE_NAME}",
            "entity_type": "Signage",
            "transport": "HTTP",
            "protocol": "PDI-IoTA-JSON",
            "apikey": "SignKey",
            "endpoint": "http://${IoT_Device_Flask}:${IoT_Deivce_Flask_Port}/command",
            "commands": [
                {
                    "name": "listAssets",
                    "type": "command"
                },
                {
                    "name": "createAsset",
                    "type": "command"
                },
                {
                    "name": "deleteAsset",
                    "type": "command"
                },
                {
                    "name": "updatePlaylistOrder",
                    "type": "command"
                },
                {
                    "name": "updateAssetPut",
                    "type": "command"
                },
                {
                    "name": "updateAssetPatch",
                    "type": "command"
                }
            ],
            "attributes": [
                { "object_id": "status", "name": "status", "type": "Text" },
                { "object_id": "displayUrl", "name": "displayUrl", "type": "Text" }
            ]
        }
    ]
}
EOF
)



curl -iX POST "http://${IOTA_HOST}:${IOTA_NORTH_PORT}/iot/devices" \
-H "Content-Type: application/json" \
-H "${HEADER_FIWARE_SERVICE}" \
-H "${HEADER_FIWARE_SERVICEPATH}" \
--data-raw "${PAYLOAD}"

echo -e "\nDone. If status code is 200, the heartbeat was sent successfully."
