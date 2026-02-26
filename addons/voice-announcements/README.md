# Add-on: Voice Announcements

Optional extension for ClawTutor that adds voice announcements via Bluetooth speaker.

## Requirements

- **Bluetooth speaker** paired with the Pi
- Speaker must be **in Bluetooth range** of the Pi (~10m)
- Internet connection (for Google TTS)

## Installation

### 1. Pair Bluetooth Speaker

```bash
bluetoothctl scan on
# Wait for speaker to appear, note the MAC address
bluetoothctl pair XX:XX:XX:XX:XX:XX
bluetoothctl trust XX:XX:XX:XX:XX:XX
bluetoothctl connect XX:XX:XX:XX:XX:XX
```

### 2. Set as Default Audio Output

The speaker should auto-set as default. Verify with:
```bash
wpctl status
# Look for * next to your speaker under Sinks
```

### 3. Install Google TTS

```bash
pip3 install --user --break-system-packages gtts
```

### 4. Copy Script

```bash
cp addons/voice-announcements/announce.sh scripts/
chmod +x scripts/announce.sh
```

## Usage

```bash
# German (default)
./scripts/announce.sh "Max, Zeit fürs Mathe-Quiz!"

# English
./scripts/announce.sh "Time for your English quiz!" en

# Other languages: fr, es, it, ...
```

## Integration Ideas

### Quiz Reminders (Cron)
```json
{
  "schedule": { "kind": "cron", "expr": "0 16 * * 1-5" },
  "payload": {
    "kind": "systemEvent", 
    "text": "Run: ./scripts/announce.sh 'Zeit fürs Quiz!'"
  }
}
```

### Screen Time Warnings
When balance runs low, announce it.

### Session End
"Deine TV-Zeit ist um!"

## Limitations

- **Range:** Speaker must stay near the Pi
- **Latency:** ~2-3 seconds for TTS generation
- **Quality:** Google TTS is decent but robotic
- **Offline:** Requires internet (no local TTS)

## Upgrading Voice Quality

For better voices, consider:
- **ElevenLabs** (realistic, paid)
- **OpenAI TTS** (good quality, paid)
- **Piper** (local, free, requires setup)

Configure in the script or use OpenClaw's built-in `tts` tool.
