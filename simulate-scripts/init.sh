#!/bin/bash

# set project root directory
PROJECT_DIR=$(dirname "$0")

# Check if DEVICE_ID and DEVICE_NAME are set, if not, prompt for input
if [ ! -f "$PROJECT_DIR/device.env" ]; then
    echo "Input required to set up the device."
    read -p "Device ID: " DEVICE_ID
    read -p "Device Name: " DEVICE_NAME

    # Store the device information in device.env file
    echo "export DEVICE_ID=${DEVICE_ID}" > "$PROJECT_DIR/device.env"
    echo "export DEVICE_NAME=${DEVICE_NAME}" >> "$PROJECT_DIR/device.env"

    echo "Info saved to device.env"
else
    echo "Using existing device settings: DEVICE_ID=$DEVICE_ID, DEVICE_NAME=$DEVICE_NAME"
fi

source "$PROJECT_DIR/config.sh"
source "$PROJECT_DIR/device.env"

# Executing setup scripts in project/setup directory
echo "Initializing setup scripts..."
bash "$PROJECT_DIR/setup/provision_service_group.sh"
echo ""
bash "$PROJECT_DIR/setup/register_subscription.sh"
echo ""
bash "$PROJECT_DIR/setup/provision_device.sh"

# Set up cron job to run send_heartbeat.sh every 2 minutes
echo "Setting up cron job for heartbeat..."
CRON_JOB="*/2 * * * * $PROJECT_DIR/jobs/send_heartbeat.sh"
CRON_EXISTS=$(crontab -l 2>/dev/null | grep -F "$CRON_JOB")

if [ -z "$CRON_EXISTS" ]; then
    echo "Adding heartbeat cron job to run every 2 minutes"
    (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
else
    echo "Cron job already exists."
fi

echo "Initialization complete! The system is configured and running."