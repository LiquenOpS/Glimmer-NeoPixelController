#!/bin/bash
# send_heartbeat.sh - Run this periodically via cron job.

source ../config.sh

if [ -z "$1" ]; then
  echo "Usage: $0 <device-id>"
  exit 1
fi

DEVICE_ID=$1

curl -s -o /dev/null -w "%{http_code}" -L -X POST "http://${HOST}:${IOTA_SOUTH_PORT}/iot/json?i=${DEVICE_ID}&k=sign" \
-H "${HEADER_CONTENT_TYPE}" \
--data-raw '{"status":"online"}'

echo "Done\n"
