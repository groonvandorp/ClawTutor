#!/bin/bash
# TV-Session starten/beenden
# Usage: tv-session.sh start <kind> <tv> <minuten>
#        tv-session.sh end <session_id>
#        tv-session.sh check  (prüft abgelaufene Sessions)

SCRIPT_DIR="$(dirname "$0")"
DB_SCRIPT="$SCRIPT_DIR/screentime-db.py"
TV_SCRIPT="$SCRIPT_DIR/appletv-access.sh"

case "$1" in
    start)
        KIND="$2"
        TV="$3"
        MINUTES="$4"
        
        if [ -z "$KIND" ] || [ -z "$TV" ] || [ -z "$MINUTES" ]; then
            echo "Usage: tv-session.sh start <kind> <tv> <minuten>"
            exit 1
        fi
        
        # Session in DB starten (prüft Guthaben, zieht ab)
        OUTPUT=$(python3 "$DB_SCRIPT" session start "$KIND" "$TV" "$MINUTES" 2>&1)
        EXIT_CODE=$?
        
        echo "$OUTPUT"
        
        if [ $EXIT_CODE -ne 0 ]; then
            exit 1
        fi
        
        # Session-ID extrahieren
        SESSION_ID=$(echo "$OUTPUT" | grep "Session-ID:" | awk '{print $NF}')
        
        # TV freischalten
        "$TV_SCRIPT" allow "$TV"
        
        echo "🆔 Session-ID: $SESSION_ID"
        echo "⏰ Läuft $MINUTES Minuten"
        ;;
        
    end)
        SESSION_ID="$2"
        
        if [ -z "$SESSION_ID" ]; then
            echo "Usage: tv-session.sh end <session_id>"
            exit 1
        fi
        
        # TV ermitteln aus Session
        TV=$(python3 -c "
import sys
sys.path.insert(0, '$SCRIPT_DIR')
from importlib.util import spec_from_loader, module_from_spec
import sqlite3
conn = sqlite3.connect('$SCRIPT_DIR/../data/screentime.db')
row = conn.execute('SELECT tv FROM tv_sessions WHERE id = ?', ($SESSION_ID,)).fetchone()
print(row[0] if row else '')
conn.close()
")
        
        if [ -z "$TV" ]; then
            echo "❌ Session $SESSION_ID nicht gefunden"
            exit 1
        fi
        
        # Session beenden
        python3 "$DB_SCRIPT" session end "$SESSION_ID"
        
        # TV sperren
        "$TV_SCRIPT" block "$TV"
        
        echo "📺 Session $SESSION_ID beendet, $TV gesperrt"
        ;;
        
    check)
        # Abgelaufene Sessions finden und beenden
        python3 -c "
import sqlite3
import subprocess
import os

db_path = '$SCRIPT_DIR/../data/screentime.db'
tv_script = '$TV_SCRIPT'

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row

expired = conn.execute('''
    SELECT * FROM tv_sessions 
    WHERE status = \"active\" AND ends_at < datetime(\"now\", \"localtime\")
''').fetchall()

if not expired:
    print('✅ Keine abgelaufenen Sessions')
else:
    for session in expired:
        print(f'⏰ Beende Session #{session[\"id\"]}: {session[\"kind\"]} → {session[\"tv\"]}')
        
        # TV sperren
        subprocess.run([tv_script, 'block', session['tv']], check=True)
        
        # Session als beendet markieren
        conn.execute('UPDATE tv_sessions SET status = \"ended\" WHERE id = ?', (session['id'],))
    
    conn.commit()
    print(f'✅ {len(expired)} Session(s) beendet')

conn.close()
"
        ;;
        
    *)
        echo "Usage: tv-session.sh <start|end|check> ..."
        exit 1
        ;;
esac
