#!/bin/bash

source ./config.sh

if [ -z "$1" ]; then
  echo "Usage: $0 <device-id>"
  exit 1
fi

DEVICE_ID=$1

echo "Simulating heartbeat for device: ${DEVICE_ID}"
echo "----------------------------------------------"

curl -s -o /dev/null -w "%{http_code}" -L -X POST "http://${HOST}:${IOTA_SOUTH_PORT}/iot/json?i=${DEVICE_ID}&k=sign" \
-H "${HEADER_CONTENT_TYPE}" \
--data-raw '{
    "claimed": false,
    "currentUrl": "about:blank"
}'

echo -e "\nDone. If status code is 200, the heartbeat was sent successfully."
