#!/usr/bin/env bash
set -e

RULE_FILE="/etc/udev/rules.d/50-respeaker.rules"
RULE_CONTENT='SUBSYSTEM=="usb", ATTR{idVendor}=="2886", ATTR{idProduct}=="0018", MODE:="0666"'

echo "Checking ReSpeaker udev rule at $RULE_FILE"

if [ -f "$RULE_FILE" ]; then
  echo "  -> Rule already exists, nothing to do."
  exit 0
fi

echo "Creating udev rule for ReSpeaker..."
echo "$RULE_CONTENT" | sudo tee "$RULE_FILE" > /dev/null

echo "Reloading udev rules..."
sudo udevadm control --reload-rules
sudo udevadm trigger

echo "Done. You may need to replug the ReSpeaker."
