#!/bin/bash

# =================================================================
# Script to List all provisioned Service Groups in the IoT Agent
# =================================================================

source ../config.sh

echo "Listing all existing Service Groups for service [${FIWARE_SERVICE}]..."
echo "------------------------------------------------------------------"

curl -s -L -X GET "http://${HOST}:1026/v2/entities" \
  -H "${HEADER_FIWARE_SERVICE}" \
  -H "${HEADER_FIWARE_SERVICEPATH}" | jq
