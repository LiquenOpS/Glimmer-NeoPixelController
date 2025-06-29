#!/bin/bash

export HOST="localhost"
export ORION_PORT="1026"
export IOTA_NORTH_PORT="4041"
export IOTA_SOUTH_PORT="7896"

export FIWARE_SERVICE="openiot"
export FIWARE_SERVICEPATH="/"

export HEADER_CONTENT_TYPE="Content-Type: application/json"
export HEADER_FIWARE_SERVICE="fiware-service: ${FIWARE_SERVICE}"
export HEADER_FIWARE_SERVICEPATH="fiware-servicepath: ${FIWARE_SERVICEPATH}"
