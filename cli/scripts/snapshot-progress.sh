#!/bin/bash
# Daily snapshot of tutor progress and screentime files
# Saves JSON log with timestamps for history tracking

SNAPSHOT_DIR="$HOME/.openclaw/workspace/snapshots"
DATE=$(date +%Y-%m-%d)
TIME=$(date +%H:%M)
mkdir -p "$SNAPSHOT_DIR"

OUTFILE="$SNAPSHOT_DIR/progress-$DATE.json"

# Workspace paths — adjust to match your setup
WS_KID1="$HOME/.openclaw/workspace-tutor-kid1"
WS_KID2="$HOME/.openclaw/workspace-tutor-kid2"

# Build JSON snapshot
cat > "$OUTFILE" <<EOF
{
  "date": "$DATE",
  "time": "$TIME",
  "kid2": {
    "progress_mathe": $(python3 -c "
import json, re
with open('$WS_KID2/PROGRESS.md') as f:
    content = f.read()
print(json.dumps(content))
" 2>/dev/null || echo '""'),
    "progress_english": $(python3 -c "
import json
try:
    with open('$WS_KID2/PROGRESS-ENGLISH.md') as f:
        print(json.dumps(f.read()))
except: print('\"\"')
" 2>/dev/null || echo '""'),
    "screentime": $(python3 -c "
import json
with open('$WS_KID2/SCREENTIME.md') as f:
    print(json.dumps(f.read()))
" 2>/dev/null || echo '""')
  },
  "kid1": {
    "progress_mathe": $(python3 -c "
import json
with open('$WS_KID1/PROGRESS.md') as f:
    print(json.dumps(f.read()))
" 2>/dev/null || echo '""'),
    "progress_english": $(python3 -c "
import json
try:
    with open('$WS_KID1/PROGRESS-ENGLISH.md') as f:
        print(json.dumps(f.read()))
except: print('\"\"')
" 2>/dev/null || echo '""'),
    "screentime": $(python3 -c "
import json
with open('$WS_KID1/SCREENTIME.md') as f:
    print(json.dumps(f.read()))
" 2>/dev/null || echo '""')
  }
}
EOF

echo "Snapshot saved: $OUTFILE"
