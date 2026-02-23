#!/usr/bin/env python3
"""
Screentime Budget Database
Verwaltet Bildschirmzeit-Guthaben für Kinder.

Usage:
  screentime-db.py init                          # DB initialisieren
  screentime-db.py balance <kind>                # Guthaben anzeigen
  screentime-db.py add <kind> <minuten> <grund>  # Zeit gutschreiben
  screentime-db.py spend <kind> <minuten> <grund> # Zeit abziehen
  screentime-db.py history <kind> [limit]        # Transaktionen anzeigen
  screentime-db.py session start <kind> <tv> <minuten>  # TV-Session starten
  screentime-db.py session end <session_id>      # TV-Session beenden
  screentime-db.py session active                # Aktive Sessions anzeigen
  screentime-db.py session check                 # Abgelaufene Sessions prüfen
"""

import sqlite3
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "screentime.db"

def get_db():
    """Verbindung zur Datenbank herstellen."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Datenbank-Schema erstellen."""
    conn = get_db()
    conn.executescript("""
        -- Guthaben pro Kind
        CREATE TABLE IF NOT EXISTS budget (
            kind TEXT PRIMARY KEY,
            balance_minutes INTEGER DEFAULT 0,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Transaktions-Historie
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kind TEXT NOT NULL,
            amount_minutes INTEGER NOT NULL,  -- positiv = verdient, negativ = verbraucht
            reason TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        
        -- Aktive TV-Sessions
        CREATE TABLE IF NOT EXISTS tv_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kind TEXT NOT NULL,
            tv TEXT NOT NULL,  -- beamer, lcd, wohnzimmer
            minutes INTEGER NOT NULL,
            started_at TEXT DEFAULT CURRENT_TIMESTAMP,
            ends_at TEXT NOT NULL,
            cron_job_id TEXT,  -- ID des Cron-Jobs für Auto-Off
            status TEXT DEFAULT 'active'  -- active, ended, cancelled
        );
        
        -- Indizes
        CREATE INDEX IF NOT EXISTS idx_transactions_kind ON transactions(kind);
        CREATE INDEX IF NOT EXISTS idx_sessions_status ON tv_sessions(status);
        CREATE INDEX IF NOT EXISTS idx_sessions_ends_at ON tv_sessions(ends_at);
    """)
    conn.commit()
    conn.close()
    print("✅ Datenbank initialisiert:", DB_PATH)

def get_balance(kind: str) -> int:
    """Aktuelles Guthaben eines Kindes abfragen."""
    conn = get_db()
    row = conn.execute("SELECT balance_minutes FROM budget WHERE kind = ?", (kind.lower(),)).fetchone()
    conn.close()
    return row["balance_minutes"] if row else 0

def add_time(kind: str, minutes: int, reason: str) -> int:
    """Zeit gutschreiben. Gibt neues Guthaben zurück."""
    kind = kind.lower()
    conn = get_db()
    
    # Budget aktualisieren oder erstellen
    conn.execute("""
        INSERT INTO budget (kind, balance_minutes, updated_at)
        VALUES (?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(kind) DO UPDATE SET
            balance_minutes = balance_minutes + ?,
            updated_at = CURRENT_TIMESTAMP
    """, (kind, minutes, minutes))
    
    # Transaktion loggen
    conn.execute("""
        INSERT INTO transactions (kind, amount_minutes, reason)
        VALUES (?, ?, ?)
    """, (kind, minutes, reason))
    
    conn.commit()
    new_balance = conn.execute("SELECT balance_minutes FROM budget WHERE kind = ?", (kind,)).fetchone()["balance_minutes"]
    conn.close()
    
    return new_balance

def spend_time(kind: str, minutes: int, reason: str) -> tuple[bool, int]:
    """
    Zeit abziehen. 
    Returns: (success, new_balance)
    Schlägt fehl wenn nicht genug Guthaben.
    """
    kind = kind.lower()
    current = get_balance(kind)
    
    if current < minutes:
        return False, current
    
    conn = get_db()
    
    conn.execute("""
        UPDATE budget 
        SET balance_minutes = balance_minutes - ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE kind = ?
    """, (minutes, kind))
    
    conn.execute("""
        INSERT INTO transactions (kind, amount_minutes, reason)
        VALUES (?, ?, ?)
    """, (kind, -minutes, reason))
    
    conn.commit()
    new_balance = conn.execute("SELECT balance_minutes FROM budget WHERE kind = ?", (kind,)).fetchone()["balance_minutes"]
    conn.close()
    
    return True, new_balance

def get_history(kind: str, limit: int = 10) -> list[dict]:
    """Transaktions-Historie abrufen."""
    conn = get_db()
    rows = conn.execute("""
        SELECT amount_minutes, reason, created_at
        FROM transactions
        WHERE kind = ?
        ORDER BY created_at DESC
        LIMIT ?
    """, (kind.lower(), limit)).fetchall()
    conn.close()
    return [dict(row) for row in rows]

def start_session(kind: str, tv: str, minutes: int) -> tuple[bool, str, int]:
    """
    TV-Session starten.
    Returns: (success, message, session_id oder balance)
    """
    kind = kind.lower()
    tv = tv.lower()
    
    # Guthaben prüfen
    current = get_balance(kind)
    if current < minutes:
        return False, f"Nicht genug Guthaben ({current} Min verfügbar, {minutes} Min angefragt)", current
    
    # Aktive Session auf diesem TV prüfen
    conn = get_db()
    active = conn.execute("""
        SELECT * FROM tv_sessions 
        WHERE tv = ? AND status = 'active'
    """, (tv,)).fetchone()
    
    if active:
        conn.close()
        return False, f"TV '{tv}' ist bereits belegt bis {active['ends_at']}", 0
    
    # Zeit abziehen
    success, new_balance = spend_time(kind, minutes, f"TV-Session: {tv} ({minutes} Min)")
    if not success:
        conn.close()
        return False, "Fehler beim Abziehen der Zeit", current
    
    # Session erstellen
    ends_at = (datetime.now() + timedelta(minutes=minutes)).strftime("%Y-%m-%d %H:%M:%S")
    
    cursor = conn.execute("""
        INSERT INTO tv_sessions (kind, tv, minutes, ends_at)
        VALUES (?, ?, ?, ?)
    """, (kind, tv, minutes, ends_at))
    
    session_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return True, f"Session gestartet (endet {ends_at})", session_id

def end_session(session_id: int, status: str = "ended") -> bool:
    """Session beenden."""
    conn = get_db()
    conn.execute("""
        UPDATE tv_sessions 
        SET status = ?
        WHERE id = ?
    """, (status, session_id))
    conn.commit()
    affected = conn.total_changes
    conn.close()
    return affected > 0

def update_session_cron(session_id: int, cron_job_id: str):
    """Cron-Job-ID für Session speichern."""
    conn = get_db()
    conn.execute("""
        UPDATE tv_sessions SET cron_job_id = ? WHERE id = ?
    """, (cron_job_id, session_id))
    conn.commit()
    conn.close()

def get_active_sessions() -> list[dict]:
    """Alle aktiven Sessions abrufen."""
    conn = get_db()
    rows = conn.execute("""
        SELECT * FROM tv_sessions 
        WHERE status = 'active'
        ORDER BY ends_at
    """).fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_expired_sessions() -> list[dict]:
    """Abgelaufene aber noch aktive Sessions finden."""
    conn = get_db()
    rows = conn.execute("""
        SELECT * FROM tv_sessions 
        WHERE status = 'active' AND ends_at < datetime('now', 'localtime')
        ORDER BY ends_at
    """).fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_session(session_id: int) -> dict | None:
    """Einzelne Session abrufen."""
    conn = get_db()
    row = conn.execute("SELECT * FROM tv_sessions WHERE id = ?", (session_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

# CLI Interface
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "init":
        init_db()
    
    elif cmd == "balance":
        if len(sys.argv) < 3:
            print("Usage: screentime-db.py balance <kind>")
            sys.exit(1)
        kind = sys.argv[2]
        balance = get_balance(kind)
        print(f"💰 {kind.capitalize()}: {balance} Minuten")
    
    elif cmd == "add":
        if len(sys.argv) < 5:
            print("Usage: screentime-db.py add <kind> <minuten> <grund>")
            sys.exit(1)
        kind, minutes, reason = sys.argv[2], int(sys.argv[3]), " ".join(sys.argv[4:])
        new_balance = add_time(kind, minutes, reason)
        print(f"✅ +{minutes} Min für {kind.capitalize()} ({reason})")
        print(f"💰 Neues Guthaben: {new_balance} Minuten")
    
    elif cmd == "spend":
        if len(sys.argv) < 5:
            print("Usage: screentime-db.py spend <kind> <minuten> <grund>")
            sys.exit(1)
        kind, minutes, reason = sys.argv[2], int(sys.argv[3]), " ".join(sys.argv[4:])
        success, new_balance = spend_time(kind, minutes, reason)
        if success:
            print(f"✅ -{minutes} Min für {kind.capitalize()} ({reason})")
            print(f"💰 Neues Guthaben: {new_balance} Minuten")
        else:
            print(f"❌ Nicht genug Guthaben! Verfügbar: {new_balance} Min")
            sys.exit(1)
    
    elif cmd == "history":
        if len(sys.argv) < 3:
            print("Usage: screentime-db.py history <kind> [limit]")
            sys.exit(1)
        kind = sys.argv[2]
        limit = int(sys.argv[3]) if len(sys.argv) > 3 else 10
        history = get_history(kind, limit)
        print(f"📜 Letzte {len(history)} Transaktionen für {kind.capitalize()}:")
        for tx in history:
            sign = "+" if tx["amount_minutes"] > 0 else ""
            print(f"  {tx['created_at']}: {sign}{tx['amount_minutes']} Min — {tx['reason']}")
    
    elif cmd == "session":
        if len(sys.argv) < 3:
            print("Usage: screentime-db.py session <start|end|active|check> ...")
            sys.exit(1)
        
        subcmd = sys.argv[2]
        
        if subcmd == "start":
            if len(sys.argv) < 6:
                print("Usage: screentime-db.py session start <kind> <tv> <minuten>")
                sys.exit(1)
            kind, tv, minutes = sys.argv[3], sys.argv[4], int(sys.argv[5])
            success, message, result = start_session(kind, tv, minutes)
            if success:
                print(f"✅ {message}")
                print(f"📺 TV '{tv}' freigeschaltet für {kind.capitalize()}")
                print(f"🆔 Session-ID: {result}")
            else:
                print(f"❌ {message}")
                sys.exit(1)
        
        elif subcmd == "end":
            if len(sys.argv) < 4:
                print("Usage: screentime-db.py session end <session_id>")
                sys.exit(1)
            session_id = int(sys.argv[3])
            if end_session(session_id):
                print(f"✅ Session {session_id} beendet")
            else:
                print(f"❌ Session {session_id} nicht gefunden")
                sys.exit(1)
        
        elif subcmd == "active":
            sessions = get_active_sessions()
            if sessions:
                print(f"📺 {len(sessions)} aktive Session(s):")
                for s in sessions:
                    print(f"  #{s['id']}: {s['kind'].capitalize()} → {s['tv']} (bis {s['ends_at']})")
            else:
                print("📺 Keine aktiven Sessions")
        
        elif subcmd == "check":
            expired = get_expired_sessions()
            if expired:
                print(f"⏰ {len(expired)} abgelaufene Session(s):")
                for s in expired:
                    print(f"  #{s['id']}: {s['kind'].capitalize()} → {s['tv']} (seit {s['ends_at']})")
            else:
                print("✅ Keine abgelaufenen Sessions")
        
        else:
            print(f"Unknown session command: {subcmd}")
            sys.exit(1)
    
    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)
        sys.exit(1)
