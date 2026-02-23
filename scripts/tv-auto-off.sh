#!/bin/bash
# tv-auto-off.sh - Automatically ends expired TV sessions
# Runs every 2 minutes via cron: */2 * * * * /path/to/tv-auto-off.sh

# Configure paths for your setup:
DB_PATH="${SCREENTIME_DB:-$HOME/.openclaw/workspace/data/screentime.db}"
TV_SCRIPT="${TV_SCRIPT:-$HOME/.openclaw/workspace/scripts/appletv-access.sh}"
LOG_FILE="${LOG_FILE:-$HOME/.openclaw/workspace/logs/tv-auto-off.log}"

# Ensure log directory exists
mkdir -p "$(dirname "$LOG_FILE")"

# Get current timestamp in same format as DB
NOW=$(date '+%Y-%m-%d %H:%M:%S')

# Find expired active sessions
EXPIRED=$(sqlite3 "$DB_PATH" "SELECT id, tv FROM tv_sessions WHERE status='active' AND ends_at < '$NOW';")

if [ -z "$EXPIRED" ]; then
    # No expired sessions, exit silently
    exit 0
fi

echo "[$NOW] Checking for expired sessions..." >> "$LOG_FILE"

# Process each expired session
echo "$EXPIRED" | while IFS='|' read -r SESSION_ID TV; do
    if [ -n "$SESSION_ID" ] && [ -n "$TV" ]; then
        echo "[$NOW] Session #$SESSION_ID expired - blocking $TV" >> "$LOG_FILE"
        
        # Block the TV
        sudo "$TV_SCRIPT" block "$TV" >> "$LOG_FILE" 2>&1
        
        # Mark session as ended
        sqlite3 "$DB_PATH" "UPDATE tv_sessions SET status='ended' WHERE id=$SESSION_ID;"
        
        echo "[$NOW] Session #$SESSION_ID ended, $TV blocked" >> "$LOG_FILE"
    fi
done

echo "[$NOW] Auto-off check complete" >> "$LOG_FILE"
