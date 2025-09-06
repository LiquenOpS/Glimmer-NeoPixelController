#!/bin/bash
# send_heartbeat.sh - Run this periodically via cron job.

source ../config.sh

if [ -z "$1" ]; then
  echo "Usage: $0 <device-id>"
  exit 1
fi

DEVICE_ID=$1

curl -s  -X POST "http://${IOTA_HOST}:${IOTA_SOUTH_PORT}/iot/json?k=SignKey&i=${DEVICE_ID}" \
-H "${HEADER_CONTENT_TYPE}" \
--data-raw '{"status":"online"}'

echo "Done\n"
