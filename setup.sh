#!/usr/bin/env bash
#
# setup.sh - Install Morning Briefing app to launch on macOS startup
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PLIST_SRC="$SCRIPT_DIR/com.morningbriefing.plist"
PLIST_NAME="com.morningbriefing.plist"
LAUNCH_DIR="$HOME/Library/LaunchAgents"
PLIST_DEST="$LAUNCH_DIR/$PLIST_NAME"
APP_SCRIPT="$SCRIPT_DIR/morning_briefing.py"

echo "=== Morning Briefing Setup ==="
echo ""

# 1. Install Python dependencies
echo "[1/4] Installing Python dependencies..."
python3 -m pip install --quiet -r "$SCRIPT_DIR/requirements.txt"
echo "      Done."

# 2. Find the python3 path
PYTHON_PATH="$(which python3)"
echo "[2/4] Using Python at: $PYTHON_PATH"

# 3. Create the LaunchAgent plist from template
echo "[3/4] Creating LaunchAgent..."
mkdir -p "$LAUNCH_DIR"

sed \
    -e "s|__PYTHON_PATH__|$PYTHON_PATH|g" \
    -e "s|__SCRIPT_PATH__|$APP_SCRIPT|g" \
    -e "s|__HOME__|$HOME|g" \
    "$PLIST_SRC" > "$PLIST_DEST"

echo "      Installed plist to: $PLIST_DEST"

# 4. Load the agent
echo "[4/4] Loading LaunchAgent..."
# Unload first if it already exists (ignore errors)
launchctl unload "$PLIST_DEST" 2>/dev/null || true
launchctl load "$PLIST_DEST"
echo "      Loaded."

echo ""
echo "=== Setup complete! ==="
echo "Morning Briefing will now launch automatically on login."
echo ""
echo "To test it right now, run:"
echo "  python3 $APP_SCRIPT"
echo ""
echo "To uninstall, run:"
echo "  bash $SCRIPT_DIR/uninstall.sh"
