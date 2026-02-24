#!/usr/bin/env python3
"""
ClawTutor Music Receiver — Läuft auf JarvisPI
Empfängt MQTT-Sessions vom Musik-Pi und vergibt Screen-Time.
"""

import paho.mqtt.client as mqtt
import json
import subprocess
import sqlite3
from datetime import datetime, date
from pathlib import Path

# ── Konfiguration ────────────────────────────────────────────────
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC_SESSION = "clawtutor/music/session"
MQTT_TOPIC_NOTES = "clawtutor/music/notes"

# Screentime DB (bestehendes Plugin)
SCREENTIME_DB = Path("/home/jarvis/.openclaw/plugins/screentime/data/screentime.db")

# Music Sessions DB
MUSIC_DB = Path("/home/jarvis/.openclaw/workspace/data/music_sessions.db")

# Screen-Time Multiplikatoren
BASE_MINUTES_PER_PRACTICE = 2.0  # 1 Min üben = 2 Min Screen-Time
RHYTHM_BONUS_THRESHOLD = 75     # Ab 75/100 Rhythmus gibt's Bonus
RHYTHM_BONUS = 0.25             # +25% bei gutem Rhythmus
STREAK_BONUS_DAYS = 3           # Ab 3 Tagen Streak
STREAK_BONUS = 0.20             # +20% Streak-Bonus

# Kinder-Mapping
CHILDREN = {
    "emma": "+49123456789",
    "max": "+49123456790",
}
PARENT_NUMBER = "+49123456788"
# ────────────────────────────────────────────────────────────────


def init_music_db():
    """Erstellt Music Sessions DB wenn nötig."""
    MUSIC_DB.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(MUSIC_DB)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            child TEXT NOT NULL,
            date TEXT NOT NULL,
            duration_min REAL NOT NULL,
            notes_played INTEGER DEFAULT 0,
            rhythm_score INTEGER DEFAULT 0,
            screen_time_earned REAL NOT NULL,
            bonuses TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()
    print(f"✅ Music DB ready: {MUSIC_DB}")


def get_streak(child: str) -> int:
    """Wie viele aufeinanderfolgende Tage hat das Kind geübt?"""
    conn = sqlite3.connect(MUSIC_DB)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("""
        SELECT DISTINCT date FROM sessions
        WHERE child = ?
        ORDER BY date DESC
        LIMIT 30
    """, (child,)).fetchall()
    conn.close()

    if not rows:
        return 0

    streak = 0
    today = date.today()
    for i, row in enumerate(rows):
        expected = str(today.replace(day=today.day - i))
        if row["date"] == expected:
            streak += 1
        else:
            break
    return streak


def calc_screen_time(duration_min: float, rhythm_score: int, child: str) -> dict:
    """Berechnet Screen-Time mit Boni."""
    multiplier = BASE_MINUTES_PER_PRACTICE
    bonuses = []

    # Rhythmus-Bonus
    if rhythm_score >= RHYTHM_BONUS_THRESHOLD:
        multiplier += RHYTHM_BONUS
        bonuses.append(f"Rhythmus {rhythm_score}/100 → +{int(RHYTHM_BONUS*100)}%")

    # Streak-Bonus
    streak = get_streak(child)
    if streak >= STREAK_BONUS_DAYS:
        multiplier += STREAK_BONUS
        bonuses.append(f"{streak}-Tage-Streak → +{int(STREAK_BONUS*100)}%")

    screen_time = round(duration_min * multiplier)
    
    return {
        "screen_time": screen_time,
        "multiplier": multiplier,
        "bonuses": bonuses,
        "streak": streak
    }


def save_session(child: str, data: dict, result: dict):
    """Speichert Session in Music DB."""
    conn = sqlite3.connect(MUSIC_DB)
    conn.execute("""
        INSERT INTO sessions (child, date, duration_min, notes_played, rhythm_score, screen_time_earned, bonuses)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        child,
        str(date.today()),
        data.get("duration_min", 0),
        data.get("notes_played", 0),
        data.get("rhythm_score", 0),
        result["screen_time"],
        json.dumps(result["bonuses"])
    ))
    conn.commit()
    conn.close()


def add_screentime(child: str, minutes: int, reason: str):
    """Fügt Screen-Time über das screentime Plugin hinzu."""
    try:
        # Nutze das native screentime Plugin via CLI
        cmd = [
            "openclaw", "tool", "screentime_add",
            "--child", child,
            "--minutes", str(minutes),
            "--reason", reason
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print(f"✅ Screentime: +{minutes} Min für {child}")
        else:
            print(f"⚠️ Screentime Fehler: {result.stderr}")
            # Fallback: direkt in DB schreiben
            add_screentime_direct(child, minutes, reason)
    except Exception as e:
        print(f"⚠️ Screentime CLI Fehler: {e}")
        add_screentime_direct(child, minutes, reason)


def add_screentime_direct(child: str, minutes: int, reason: str):
    """Fallback: Direkt in Screentime DB schreiben."""
    if not SCREENTIME_DB.exists():
        print(f"⚠️ Screentime DB nicht gefunden: {SCREENTIME_DB}")
        return
    
    conn = sqlite3.connect(SCREENTIME_DB)
    # Budget erhöhen
    conn.execute("""
        INSERT INTO budget (child, balance) VALUES (?, ?)
        ON CONFLICT(child) DO UPDATE SET balance = balance + ?
    """, (child, minutes, minutes))
    
    # Transaction loggen
    conn.execute("""
        INSERT INTO transactions (child, amount, reason, source)
        VALUES (?, ?, ?, 'music')
    """, (child, minutes, reason))
    
    conn.commit()
    conn.close()
    print(f"✅ Screentime (direkt): +{minutes} Min für {child}")


def send_whatsapp(to: str, message: str):
    """Sendet WhatsApp über OpenClaw message tool."""
    try:
        cmd = [
            "openclaw", "message", "send",
            "--to", to,
            "--message", message,
            "--channel", "whatsapp",
            "--account", "assistant"
        ]
        subprocess.run(cmd, capture_output=True, timeout=30)
        print(f"📱 WhatsApp an {to}")
    except Exception as e:
        print(f"⚠️ WhatsApp Fehler: {e}")


def build_child_message(child: str, data: dict, result: dict) -> str:
    """Baut Nachricht fürs Kind."""
    duration = data.get("duration_min", 0)
    rhythm = data.get("rhythm_score", 0)
    notes = data.get("notes_played", 0)
    screen_time = result["screen_time"]
    streak = result["streak"]

    # Rhythmus-Feedback
    if rhythm >= 85:
        rhythm_text = "Dein Rhythmus war richtig sauber! 🎯"
    elif rhythm >= 70:
        rhythm_text = "Guter Rhythmus! 👍"
    elif rhythm >= 50:
        rhythm_text = "Rhythmus wird besser! 📈"
    else:
        rhythm_text = "Weiter üben - der Rhythmus kommt! 💪"

    # Streak
    streak_text = f"\n🔥 {streak} Tage in Folge!" if streak >= 3 else ""

    # Boni
    bonus_text = ""
    if result["bonuses"]:
        bonus_text = "\n✨ " + ", ".join(result["bonuses"])

    return (
        f"🎹 Super gemacht, {child.capitalize()}!\n\n"
        f"Du hast {duration:.0f} Min Klavier geübt und {notes} Noten gespielt.\n"
        f"{rhythm_text}"
        f"{streak_text}"
        f"{bonus_text}\n\n"
        f"⏱️ Du hast dir **{screen_time} Min Screen-Time** verdient!"
    )


def build_parent_message(child: str, data: dict, result: dict) -> str:
    """Baut Nachricht für Eltern."""
    duration = data.get("duration_min", 0)
    rhythm = data.get("rhythm_score", 0)
    notes = data.get("notes_played", 0)
    screen_time = result["screen_time"]
    streak = result["streak"]

    return (
        f"🎹 Musik-Report: {child.capitalize()}\n"
        f"────────────────\n"
        f"⏱️ Dauer: {duration:.0f} Min\n"
        f"🎵 Noten: {notes}\n"
        f"🥁 Rhythmus: {rhythm}/100\n"
        f"🔥 Streak: {streak} Tage\n"
        f"────────────────\n"
        f"Screen-Time: +{screen_time} Min"
    )


def on_message(client, userdata, msg):
    """Verarbeitet eingehende MQTT-Nachrichten."""
    try:
        if msg.topic == MQTT_TOPIC_SESSION:
            data = json.loads(msg.payload.decode())
            child = data.get("child", "").lower()

            print(f"\n{'='*40}")
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Session empfangen:")
            print(f"  Kind: {child}")
            print(f"  Dauer: {data.get('duration_min', 0):.1f} Min")
            print(f"  Noten: {data.get('notes_played', 0)}")
            print(f"  Rhythmus: {data.get('rhythm_score', 0)}/100")

            if child not in CHILDREN:
                print(f"  ⚠️ Unbekanntes Kind: {child}")
                return

            # Screen-Time berechnen
            result = calc_screen_time(
                data.get("duration_min", 0),
                data.get("rhythm_score", 0),
                child
            )
            print(f"  Screen-Time: {result['screen_time']} Min")
            print(f"  Boni: {result['bonuses']}")

            # Speichern
            save_session(child, data, result)

            # Screen-Time gutschreiben
            reason = f"Klavier üben ({data.get('duration_min', 0):.0f} Min, Rhythmus {data.get('rhythm_score', 0)}/100)"
            add_screentime(child, result["screen_time"], reason)

            # WhatsApp senden
            child_msg = build_child_message(child, data, result)
            parent_msg = build_parent_message(child, data, result)

            send_whatsapp(CHILDREN[child], child_msg)
            send_whatsapp(PARENT_NUMBER, parent_msg)

            print(f"  ✅ Abgeschlossen!")
            print(f"{'='*40}\n")

        elif msg.topic == MQTT_TOPIC_NOTES:
            # Live-Noten (optional für Echtzeit-Anzeige)
            data = json.loads(msg.payload.decode())
            if data.get("type") == "note_on":
                note = data.get("note_name", "?")
                print(f"🎵 {note}", end=" ", flush=True)

    except Exception as e:
        print(f"❌ Fehler: {e}")


def on_connect(client, userdata, flags, rc):
    """MQTT Connect Handler."""
    if rc == 0:
        print(f"✅ MQTT verbunden mit {MQTT_BROKER}:{MQTT_PORT}")
        client.subscribe(MQTT_TOPIC_SESSION)
        client.subscribe(MQTT_TOPIC_NOTES)
        print(f"📡 Lausche auf:")
        print(f"   - {MQTT_TOPIC_SESSION}")
        print(f"   - {MQTT_TOPIC_NOTES}")
    else:
        print(f"❌ MQTT Fehler: {rc}")


def main():
    print("🎹 ClawTutor Music Receiver startet...")
    print(f"   MQTT: {MQTT_BROKER}:{MQTT_PORT}")
    print(f"   Music DB: {MUSIC_DB}")
    print()

    init_music_db()

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
        print("\n✅ Bereit! Warte auf Musik-Sessions...\n")
        client.loop_forever()
    except KeyboardInterrupt:
        print("\n👋 Beende...")
    except Exception as e:
        print(f"❌ Fehler: {e}")


if __name__ == "__main__":
    main()
