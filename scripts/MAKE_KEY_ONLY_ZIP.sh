#!/usr/bin/env bash
set -euo pipefail

# This script creates a small ZIP containing only the key file, preserving the path
# Usage: bash /app/scripts/MAKE_KEY_ONLY_ZIP.sh my-new-secure-key

NEW_KEY=${1:-}
if [[ -z "${NEW_KEY}" ]]; then
  echo "Usage: $0 <NEW_KEY>"
  exit 1
fi

WORKDIR="/app/scripts/key_patch_build"
rm -rf "$WORKDIR"
mkdir -p "$WORKDIR/backend"

# Write the key file with the provided key
cat > "$WORKDIR/backend/config_app_key.py" <<EOF
# Drop-in replacement file for changing the application key
# Place inside ZIP at path: backend/config_app_key.py (overwrite existing)
APP_KEY = "${NEW_KEY}"
EOF

# Create the zip with internal path backend/config_app_key.py so it can be unzipped to replace
cd "$WORKDIR"
ZIP_OUT="key_patch.zip"
zip -r "$ZIP_OUT" backend >/dev/null

# Move zip to scripts folder for easy download
mv "$ZIP_OUT" /app/scripts/

echo "Created /app/scripts/key_patch.zip with APP_KEY='${NEW_KEY}'"
echo "To apply on target app folder: unzip -o key_patch.zip -d <target_app_root>"
