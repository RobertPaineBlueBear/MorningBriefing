#!/usr/bin/env bash
#
# uninstall.sh - Remove Morning Briefing from macOS startup
#
set -euo pipefail

PLIST_NAME="com.morningbriefing.plist"
PLIST_PATH="$HOME/Library/LaunchAgents/$PLIST_NAME"

echo "=== Morning Briefing Uninstall ==="
echo ""

if [ -f "$PLIST_PATH" ]; then
    echo "Unloading LaunchAgent..."
    launchctl unload "$PLIST_PATH" 2>/dev/null || true
    rm "$PLIST_PATH"
    echo "Removed: $PLIST_PATH"
else
    echo "LaunchAgent not found at $PLIST_PATH (already uninstalled?)"
fi

echo ""
echo "Done. Morning Briefing will no longer launch on startup."
echo "The app files in this directory have not been deleted."
