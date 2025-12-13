#!/bin/bash
set -e

# Default MuQ source path (sibling directory)
MUQ_SRC_PATH="../MuQ"
DEST_PATH="backend/muq_pkg"

echo "Comparing MuQ source path: $MUQ_SRC_PATH"

if [ ! -d "$MUQ_SRC_PATH" ]; then
    echo "Error: MuQ source directory not found at $MUQ_SRC_PATH"
    echo "Please ensure the MuQ repository is cloned as a sibling to MUSEED."
    exit 1
fi

echo "Cleaning destination: $DEST_PATH"
rm -rf "$DEST_PATH"
mkdir -p "$DEST_PATH"

echo "Copying MuQ source code..."
# Copy source directory
cp -r "$MUQ_SRC_PATH/src" "$DEST_PATH/"
# Copy setup files
cp "$MUQ_SRC_PATH/setup.py" "$DEST_PATH/"
cp "$MUQ_SRC_PATH/requirements.txt" "$DEST_PATH/"
# Copy README (sometimes needed for setup.py long_description)
cp "$MUQ_SRC_PATH/README.md" "$DEST_PATH/"

# Remove potential garbage
find "$DEST_PATH" -name "__pycache__" -type d -exec rm -rf {} +
find "$DEST_PATH" -name "*.pyc" -delete
find "$DEST_PATH" -name ".git" -type d -exec rm -rf {} +

echo "MuQ vendoring complete at $DEST_PATH"
echo "You can now build the Docker image."
