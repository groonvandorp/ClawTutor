#!/bin/bash
# announce.sh - Text-to-Speech Ansagen über Bluetooth-Speaker
# Usage: ./announce.sh "Nachricht" [sprache]
#
# Beispiele:
#   ./announce.sh "Max, Zeit fürs Mathe-Quiz!"
#   ./announce.sh "Time for your English quiz!" en
#
# Nutzt Google TTS (gtts) - kostenlos, kein API Key nötig

MESSAGE="$1"
LANG="${2:-de}"  # de, en, fr, es, ...

if [ -z "$MESSAGE" ]; then
    echo "Usage: $0 \"Nachricht\" [sprache]"
    echo "Sprachen: de (default), en, fr, es, ..."
    exit 1
fi

TTS_FILE=$(mktemp /tmp/announce-XXXXXX.mp3)

# Generate TTS via Google TTS
gtts-cli "$MESSAGE" -l "$LANG" -o "$TTS_FILE" 2>/dev/null

if [ ! -s "$TTS_FILE" ]; then
    echo "Error: TTS generation failed"
    rm -f "$TTS_FILE"
    exit 1
fi

# Play via ffplay (uses default PipeWire sink = Bluetooth speaker)
ffplay -nodisp -autoexit -loglevel quiet "$TTS_FILE"

# Cleanup
rm -f "$TTS_FILE"
