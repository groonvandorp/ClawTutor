#!/usr/bin/env python3
"""
ClawTutor MIDI Sender — Läuft auf dem Musik-Pi (MusicPi)
Erfasst MIDI-Events vom Keyboard und sendet sie an den ClawTutor-Pi via MQTT.
"""

import mido
import paho.mqtt.client as mqtt
import json
import time
from datetime import datetime
from collections import defaultdict
import threading

# ── Konfiguration ────────────────────────────────────────────────
MQTT_BROKER = "192.168.1.100"  # ClawTutorPi
MQTT_PORT = 1883
MQTT_TOPIC_NOTES = "clawtutor/music/notes"      # Einzelne Noten (live)
MQTT_TOPIC_SESSION = "clawtutor/music/session"  # Session-Summary

# Session-Einstellungen
SESSION_TIMEOUT_SECONDS = 60  # Nach 60s Stille = Session beendet
MIN_SESSION_DURATION = 30     # Mindestens 30s für gültige Session
# ────────────────────────────────────────────────────────────────


class MusicSession:
    """Trackt eine Übungssession."""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.start_time = None
        self.last_activity = None
        self.notes_played = 0
        self.note_times = []       # Timestamps für Rhythmus-Analyse
        self.notes_held = set()    # Aktuell gehaltene Noten
        self.all_notes = []        # Alle gespielten Noten (für Analyse)
        self.child = None          # Wird beim Start gesetzt
    
    def start(self, child: str = "unknown"):
        self.reset()
        self.start_time = time.time()
        self.last_activity = self.start_time
        self.child = child
        print(f"🎹 Session gestartet für {child}")
    
    def note_on(self, note: int, velocity: int):
        now = time.time()
        if self.start_time is None:
            self.start("unknown")  # Auto-start
        
        self.last_activity = now
        self.notes_played += 1
        self.note_times.append(now)
        self.notes_held.add(note)
        self.all_notes.append({
            "note": note,
            "velocity": velocity,
            "time": now - self.start_time
        })
    
    def note_off(self, note: int):
        self.notes_held.discard(note)
        self.last_activity = time.time()
    
    def get_duration_minutes(self) -> float:
        if self.start_time is None:
            return 0
        return (self.last_activity - self.start_time) / 60
    
    def calculate_rhythm_score(self) -> int:
        """
        Berechnet einen Rhythmus-Score basierend auf der Regelmäßigkeit der Noten.
        100 = perfekt gleichmäßig, 0 = chaotisch
        """
        if len(self.note_times) < 4:
            return 50  # Nicht genug Daten
        
        # Zeitabstände zwischen aufeinanderfolgenden Noten
        intervals = []
        for i in range(1, len(self.note_times)):
            intervals.append(self.note_times[i] - self.note_times[i-1])
        
        if not intervals:
            return 50
        
        # Durchschnittliches Intervall
        avg_interval = sum(intervals) / len(intervals)
        if avg_interval == 0:
            return 50
        
        # Variationskoeffizient (niedriger = gleichmäßiger)
        variance = sum((i - avg_interval) ** 2 for i in intervals) / len(intervals)
        std_dev = variance ** 0.5
        cv = std_dev / avg_interval
        
        # In Score umwandeln (CV von 0 = 100 Punkte, CV von 1+ = ~0 Punkte)
        score = max(0, min(100, int(100 * (1 - cv))))
        return score
    
    def get_summary(self) -> dict:
        return {
            "child": self.child,
            "duration_min": round(self.get_duration_minutes(), 1),
            "notes_played": self.notes_played,
            "rhythm_score": self.calculate_rhythm_score(),
            "timestamp": datetime.now().isoformat()
        }
    
    def is_timed_out(self) -> bool:
        if self.last_activity is None:
            return False
        return (time.time() - self.last_activity) > SESSION_TIMEOUT_SECONDS
    
    def is_valid(self) -> bool:
        """Session ist gültig wenn sie mindestens MIN_SESSION_DURATION dauerte."""
        return self.get_duration_minutes() * 60 >= MIN_SESSION_DURATION


# Globale Session
session = MusicSession()
mqtt_client = None


def on_mqtt_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"✅ MQTT verbunden mit {MQTT_BROKER}")
        # Subscribe für Befehle (z.B. Kind-Auswahl)
        client.subscribe("clawtutor/music/control")
    else:
        print(f"❌ MQTT Verbindungsfehler: {rc}")


def on_mqtt_message(client, userdata, msg):
    """Empfängt Kontroll-Nachrichten (z.B. Kind-Auswahl)."""
    global session
    try:
        data = json.loads(msg.payload.decode())
        if "child" in data:
            session.child = data["child"]
            print(f"👤 Kind gesetzt: {session.child}")
        if data.get("action") == "start":
            session.start(data.get("child", "unknown"))
        elif data.get("action") == "stop":
            end_session()
    except Exception as e:
        print(f"Kontroll-Fehler: {e}")


def send_note_event(note: int, velocity: int, event_type: str):
    """Sendet einzelne Note für Live-Anzeige."""
    if mqtt_client is None:
        return
    
    payload = {
        "type": event_type,
        "note": note,
        "velocity": velocity,
        "note_name": get_note_name(note),
        "child": session.child,
        "timestamp": datetime.now().isoformat()
    }
    mqtt_client.publish(MQTT_TOPIC_NOTES, json.dumps(payload))


def get_note_name(midi_note: int) -> str:
    """Wandelt MIDI-Note in Namen um (z.B. 60 -> C4)."""
    notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    octave = (midi_note // 12) - 1
    note = notes[midi_note % 12]
    return f"{note}{octave}"


def end_session():
    """Beendet Session und sendet Summary."""
    global session
    
    if not session.is_valid():
        print(f"⏭️ Session zu kurz ({session.get_duration_minutes():.1f} min), wird verworfen")
        session.reset()
        return
    
    summary = session.get_summary()
    print(f"\n📊 Session beendet:")
    print(f"   Kind: {summary['child']}")
    print(f"   Dauer: {summary['duration_min']} Min")
    print(f"   Noten: {summary['notes_played']}")
    print(f"   Rhythmus: {summary['rhythm_score']}/100")
    
    if mqtt_client:
        mqtt_client.publish(MQTT_TOPIC_SESSION, json.dumps(summary))
        print(f"   ✅ An ClawTutor gesendet")
    
    session.reset()


def session_watchdog():
    """Überwacht Session-Timeout in separatem Thread."""
    while True:
        time.sleep(5)
        if session.start_time and session.is_timed_out():
            print("\n⏰ Session-Timeout erreicht")
            end_session()


def find_midi_device():
    """Findet das MIDI-Input-Device (Keyboard)."""
    inputs = mido.get_input_names()
    print(f"Verfügbare MIDI-Inputs: {inputs}")
    
    for name in inputs:
        if 'monologue' in name.lower():
            return name
    
    # Fallback: erstes verfügbares Device
    if inputs:
        return inputs[0]
    
    return None


def main():
    global mqtt_client
    
    print("🎹 ClawTutor MIDI Sender startet...")
    print(f"   Broker: {MQTT_BROKER}:{MQTT_PORT}")
    
    # MQTT verbinden
    mqtt_client = mqtt.Client()
    mqtt_client.on_connect = on_mqtt_connect
    mqtt_client.on_message = on_mqtt_message
    
    try:
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
        mqtt_client.loop_start()
    except Exception as e:
        print(f"⚠️ MQTT nicht erreichbar: {e}")
        print("   Arbeite offline, Sessions werden nicht gesendet")
    
    # Session-Watchdog starten
    watchdog = threading.Thread(target=session_watchdog, daemon=True)
    watchdog.start()
    
    # MIDI-Device finden
    device = find_midi_device()
    if not device:
        print("❌ Kein MIDI-Device gefunden!")
        return
    
    print(f"🎵 Verbinde mit: {device}")
    
    # MIDI-Events verarbeiten
    try:
        with mido.open_input(device) as inport:
            print("✅ Bereit! Spiel los...")
            print("-" * 40)
            
            for msg in inport:
                if msg.type == 'note_on' and msg.velocity > 0:
                    session.note_on(msg.note, msg.velocity)
                    note_name = get_note_name(msg.note)
                    print(f"🎵 {note_name} (vel: {msg.velocity})")
                    send_note_event(msg.note, msg.velocity, "note_on")
                
                elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                    session.note_off(msg.note)
                    send_note_event(msg.note, 0, "note_off")
                    
    except KeyboardInterrupt:
        print("\n👋 Beende...")
        end_session()
    except Exception as e:
        print(f"❌ Fehler: {e}")


if __name__ == "__main__":
    main()
