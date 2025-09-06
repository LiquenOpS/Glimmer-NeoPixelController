#!/bin/bash

export HOST="localhost" # orion context broker
export IOTA_HOST="localhost" # IoT Agent Json
export ODOO_HOST="localhost" # Odoo
export IoT_Device_Flask="localhost" # IoT Device Flask App

export ORION_PORT="1026"
export IOTA_NORTH_PORT="4041"
export IOTA_SOUTH_PORT="7896"
export ODOO_PORT="8069"
export IoT_Deivce_Flask_Port="5000" # IoT Device Flask App Port

export FIWARE_SERVICE="openiot"
export FIWARE_SERVICEPATH="/"

export HEADER_CONTENT_TYPE="Content-Type: application/json"
export HEADER_FIWARE_SERVICE="fiware-service: ${FIWARE_SERVICE}"
export HEADER_FIWARE_SERVICEPATH="fiware-servicepath: ${FIWARE_SERVICEPATH}"
