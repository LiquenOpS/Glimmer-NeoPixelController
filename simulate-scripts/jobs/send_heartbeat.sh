#!/bin/bash
# send_heartbeat.sh - Run this periodically via cron job.


if [ -z "$DEVICE_ID" ]; then
  echo "Error: DEVICE_ID is not set. Please make sure device.env contains the DEVICE_ID."
  exit 1
fi

curl -s  -X POST "http://${IOTA_HOST}:${IOTA_SOUTH_PORT}/iot/json?k=SignKey&i=${DEVICE_ID}" \
-H "${HEADER_CONTENT_TYPE}" \
--data-raw '{"status":"online"}'

echo "Done\n"
