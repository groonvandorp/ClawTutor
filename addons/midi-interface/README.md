# 🎹 MIDI-Interface Addon

Erweitere ClawTutor um ein MIDI-Interface für Musik-Tutoring mit echtem Keyboard-Feedback.

## Übersicht

```
┌─────────────────────┐     ┌─────────────────────┐
│     Musik-Pi        │     │    ClawTutor-Pi     │
│                     │     │                     │
│  ┌───────────────┐  │     │  ┌───────────────┐  │
│  │   Keyboard    │  │     │  │   Mosquitto   │  │
│  │   (USB MIDI)  │  │     │  │ (MQTT Broker) │  │
│  └───────┬───────┘  │     │  └───────┬───────┘  │
│          │          │     │          │          │
│  ┌───────▼───────┐  │     │  ┌───────▼───────┐  │
│  │  midi_sender  │──┼─────┼──│music_receiver │  │
│  │    (Python)   │  │ MQTT│  │   (Python)    │  │
│  └───────────────┘  │     │  └───────┬───────┘  │
│                     │     │          │          │
└─────────────────────┘     │  ┌───────▼───────┐  │
                            │  │ Melody Agent  │  │
                            │  │  (OpenClaw)   │  │
                            │  └───────────────┘  │
                            └─────────────────────┘
```

## Hardware-Anforderungen

### Musik-Pi
- Raspberry Pi 3B+ oder neuer
- USB-MIDI-Keyboard (Korg, Yamaha, Roland, etc.)
- Netzteil min. 2.5A
- WLAN-Verbindung

### ClawTutor-Pi
- Bestehende ClawTutor-Installation
- MQTT Broker (Mosquitto)

## Installation

### 1. Musik-Pi einrichten

```bash
# System updaten
sudo apt update && sudo apt install -y python3-pip python3-dev libasound2-dev

# Python-Umgebung
mkdir -p ~/clawtutor && cd ~/clawtutor
python3 -m venv venv
source venv/bin/activate
pip install mido python-rtmidi paho-mqtt

# Script kopieren und IP anpassen:
# MQTT_BROKER = "192.168.x.x"  # IP deines ClawTutor-Pi
```

### 2. Systemd Service (Musik-Pi)

```bash
sudo cp clawtutor-midi.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable clawtutor-midi
sudo systemctl start clawtutor-midi
```

### 3. MQTT Broker (ClawTutor-Pi)

```bash
sudo apt install -y mosquitto mosquitto-clients
echo -e "listener 1883 0.0.0.0\nallow_anonymous true" | sudo tee /etc/mosquitto/conf.d/clawtutor.conf
sudo systemctl restart mosquitto
sudo ufw allow 1883/tcp
```

### 4. Music Receiver (ClawTutor-Pi)

```bash
cd ~/.openclaw/workspace/scripts
python3 -m venv music-venv
source music-venv/bin/activate
pip install paho-mqtt

sudo cp music-receiver.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable music-receiver
sudo systemctl start music-receiver
```

## Keyboard-Einstellungen

### Korg (Monologue, Minilogue, etc.)
- EDIT MODE → GLOBAL → MIDI
- **MIDI Route** = USB oder USB+MIDI
- **Local** = ON

### Yamaha / Roland
- Local Control = ON
- USB MIDI aktiviert

## Screen-Time Berechnung

| Aktion | Belohnung |
|--------|-----------|
| 1 Min üben | 2 Min Screen-Time |
| Rhythmus ≥75/100 | +25% Bonus |
| Streak ≥3 Tage | +20% Bonus |

## MQTT Topics

| Topic | Beschreibung |
|-------|--------------|
| `clawtutor/music/notes` | Live-Noten |
| `clawtutor/music/session` | Session-Summary |
| `clawtutor/music/control` | Steuerung |

## Dateien

| Datei | Beschreibung |
|-------|--------------|
| `midi_sender.py` | Läuft auf Musik-Pi |
| `music_receiver.py` | Läuft auf ClawTutor-Pi |
| `clawtutor-midi.service` | Service für Musik-Pi |
| `music-receiver.service` | Service für ClawTutor-Pi |
| `templates/` | Agent-Templates (Melody) |
