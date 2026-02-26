# Melody 🎹 — Musik-Tutor Setup

## Übersicht

Melody ist der Musik-Tutor von ClawTutor. Sie kann MIDI-Daten vom Korg Monologue empfangen und den Kindern beim Klavierüben helfen.

## Architektur

```
┌─────────────────────┐     ┌─────────────────────┐
│   KorgKeyboardPI    │     │      JarvisPI       │
│   (192.168.2.30)    │     │   (192.168.2.47)    │
│                     │     │                     │
│  ┌───────────────┐  │     │  ┌───────────────┐  │
│  │ Korg Monologue│  │     │  │   Mosquitto   │  │
│  │   (USB MIDI)  │  │     │  │ (MQTT Broker) │  │
│  └───────┬───────┘  │     │  └───────┬───────┘  │
│          │          │     │          │          │
│  ┌───────▼───────┐  │     │  ┌───────▼───────┐  │
│  │  midi_sender  │──┼─────┼──│music_receiver │  │
│  │    (Python)   │  │MQTT │  │   (Python)    │  │
│  └───────────────┘  │     │  └───────┬───────┘  │
│                     │     │          │          │
└─────────────────────┘     │  ┌───────▼───────┐  │
                            │  │ Melody Agent  │  │
                            │  │  (OpenClaw)   │  │
                            │  └───────┬───────┘  │
                            │          │          │
                            │  ┌───────▼───────┐  │
                            │  │   WhatsApp    │  │
                            │  └───────────────┘  │
                            └─────────────────────┘
```

## Komponenten

### 1. KorgKeyboardPI (Musik-Pi)

**Pfad:** `/home/jarvis/clawtutor/`

- **midi_sender.py** — Liest MIDI vom Korg, sendet an MQTT
- **venv/** — Python Virtual Environment
- **Service:** `clawtutor-midi.service`

**Status prüfen:**
```bash
ssh jarvis@192.168.2.30 "systemctl status clawtutor-midi"
```

### 2. JarvisPI (ClawTutor-Pi)

**Pfad:** `/home/jarvis/.openclaw/workspace/scripts/`

- **music_receiver.py** — Empfängt MQTT, vergibt Screen-Time
- **music-venv/** — Python Virtual Environment
- **Service:** `music-receiver.service`

**Mosquitto:**
- Port: 1883
- Config: `/etc/mosquitto/conf.d/clawtutor.conf`

### 3. Melody Agent

**Workspace:** `/home/jarvis/.openclaw/workspace-melody/`

- **SOUL.md** — Persönlichkeit
- **CURRICULUM.md** — Lehrplan
- **PROGRESS.md** — Fortschritt der Kinder

## Installation

### Music Receiver Service (einmalig)

```bash
# Service installieren
sudo cp /home/jarvis/.openclaw/workspace/scripts/music-receiver.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable music-receiver
sudo systemctl start music-receiver

# Status prüfen
systemctl status music-receiver
```

### Melody Agent (einmalig)

In `/home/jarvis/.openclaw/openclaw.json`:

```json
{
  "agents": {
    "melody": {
      "workspace": "/home/jarvis/.openclaw/workspace-melody",
      "model": "anthropic/claude-sonnet-4-20250514"
    }
  }
}
```

## MQTT Topics

| Topic | Beschreibung |
|-------|--------------|
| `clawtutor/music/notes` | Live-Noten (note_on/note_off) |
| `clawtutor/music/session` | Session-Summary nach Übungsende |
| `clawtutor/music/control` | Befehle an MIDI-Sender |

## Session-Daten Format

```json
{
  "child": "olivia",
  "duration_min": 12.5,
  "notes_played": 234,
  "rhythm_score": 78,
  "timestamp": "2026-02-23T18:30:00"
}
```

## Screen-Time Berechnung

| Basis | Wert |
|-------|------|
| Pro Minute üben | 2 Min Screen-Time |
| Rhythmus ≥75 | +25% Bonus |
| Streak ≥3 Tage | +20% Bonus |

## Troubleshooting

### MIDI kommt nicht an

1. Korg eingeschaltet?
2. USB verbunden?
3. MIDI TX aktiviert am Monologue?
4. Service läuft? `systemctl status clawtutor-midi`

### MQTT-Verbindungsprobleme

1. Mosquitto läuft? `systemctl status mosquitto`
2. Port 1883 offen? `sudo ufw status`
3. Netzwerkverbindung? `ping 192.168.2.47`

### Musik-Pi instabil

- Netzteil prüfen (min. 2.5A, besser 3A)
- WLAN-Signalstärke?
- `journalctl -u clawtutor-midi -f`

## Dateien

| Datei | Ort |
|-------|-----|
| MIDI Sender | KorgKeyboardPI:`/home/jarvis/clawtutor/midi_sender.py` |
| Music Receiver | JarvisPI:`/home/jarvis/.openclaw/workspace/scripts/music_receiver.py` |
| Music DB | JarvisPI:`/home/jarvis/.openclaw/workspace/data/music_sessions.db` |
| Mosquitto Config | JarvisPI:`/etc/mosquitto/conf.d/clawtutor.conf` |
| Melody Workspace | JarvisPI:`/home/jarvis/.openclaw/workspace-melody/` |
