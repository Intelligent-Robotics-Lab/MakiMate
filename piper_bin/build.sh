#!/usr/bin/env bash
set -e

BASE_DIR="$(dirname "$0")"
BUILD_DIR="$BASE_DIR/piper_src"

# This script downloads Piper (aarch64 version) and unpacks it
echo "Downloading Piper (linux aarch64) ..."
wget -O "$BASE_DIR/piper_linux_aarch64.tar.gz" \
    https://github.com/rhasspy/piper/releases/download/v0.0.2/piper_linux_aarch64.tar.gz

echo "Extracting ..."
tar -xzf "$BASE_DIR/piper_linux_aarch64.tar.gz" -C "$BASE_DIR"

echo "Piper extracted to: $BASE_DIR"
echo "You may now configure your TTS node to point to the binary:"
echo "$BASE_DIR/piper/piper"
