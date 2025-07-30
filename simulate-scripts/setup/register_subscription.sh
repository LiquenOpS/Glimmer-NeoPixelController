source ../config.sh

curl -L -X POST "http://${HOST}:${ORION_PORT}/v2/subscriptions" \
-H "Content-Type: application/json" \
-H "${HEADER_FIWARE_SERVICE}" \
-H "${HEADER_FIWARE_SERVICEPATH}" \
--data-raw '{
  "description": "Notify Odoo when display status changes",
  "subject": {
    "entities": [
      {	
	"idPattern": ".*",
        "type": "Screen"
      }
    ],
    "condition": {
      "attrs": [
        "status"
      ]
    }
  },
  "notification": {
    "http": {
      "url": "http://odoo:8069/update_last_seen"
    },
    "attrs": [],
    "attrsFormat": "keyValues"
  }
}'

