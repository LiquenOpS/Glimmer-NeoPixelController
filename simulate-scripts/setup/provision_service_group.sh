#!/bin/bash

echo "Provisioning IoT Agent with a Service Group..."
echo "----------------------------------------------"

curl -s -o /dev/null -w "%{http_code}" -L -X POST "http://${IOTA_HOST}:${IOTA_NORTH_PORT}/iot/services" \
-H "${HEADER_CONTENT_TYPE}" \
-H "${HEADER_FIWARE_SERVICE}" \
-H "${HEADER_FIWARE_SERVICEPATH}" \
--data-raw '{
    "services": [
        {
            "apikey": "SignKey",
            "cbroker": "http://orion:1026",
            "entity_type": "Signage",
            "resource": "/iot/json"
        }
    ]
}'

echo -e "\nDone. If status code is 201, the service group was created successfully."
