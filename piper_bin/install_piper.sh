#!/usr/bin/env bash
set -e

# Resolve the directory of this script
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARBALL="$BASE_DIR/piper_linux_aarch64.tar.gz"
TARGET_DIR="$BASE_DIR/piper"

echo "Piper install script"
echo "Base dir:   $BASE_DIR"
echo "Tarball:    $TARBALL"
echo "Target dir: $TARGET_DIR"
echo

if [ ! -f "$TARBALL" ]; then
  echo "ERROR: Tarball not found at:"
  echo "  $TARBALL"
  echo "Make sure piper_linux_aarch64.tar.gz is in piper_bin/ and tracked in the repo."
  exit 1
fi

echo "Removing any existing Piper directory..."
rm -rf "$TARGET_DIR"

echo "Extracting Piper from local tarball..."
tar -xzf "$TARBALL" -C "$BASE_DIR"

if [ ! -d "$TARGET_DIR" ]; then
  echo "WARNING: After extraction, '$TARGET_DIR' was not found."
  echo "Check the contents of the tarball to see what it creates."
else
  echo "Piper extracted successfully to:"
  echo "  $TARGET_DIR"
  echo
  echo "Piper binary should be at:"
  echo "  $TARGET_DIR/piper"
fi

echo
echo "Done."
