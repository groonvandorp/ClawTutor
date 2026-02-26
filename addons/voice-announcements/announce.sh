#!/bin/bash
# announce.sh - Text-to-Speech announcements via Bluetooth speaker
# Usage: ./announce.sh "message" [language]
#
# Examples:
#   ./announce.sh "Max, time for your math quiz!"
#   ./announce.sh "Zeit fürs Mathe-Quiz!" de
#
# Uses Google TTS (gtts) - free, no API key required

MESSAGE="$1"
LANG="${2:-en}"  # en, de, fr, es, ...

if [ -z "$MESSAGE" ]; then
    echo "Usage: $0 \"message\" [language]"
    echo "Languages: en (default), de, fr, es, ..."
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
