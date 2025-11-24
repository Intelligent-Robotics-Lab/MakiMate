#!/bin/bash

echo "Installing config files..."

# Install config.txt (requires sudo)
sudo cp config.txt.example /boot/firmware/config.txt

# Install .bashrc to user home
cp bashrc.example ~/.bashrc

echo "Done! Reboot recommended."

