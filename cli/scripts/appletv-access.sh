#!/bin/bash
# AppleTV Bildschirmzeit-Kontrolle via Pi-hole API
# Usage: appletv-access.sh [block|allow|status] [all|beamer|lcd|wohnzimmer]

PIHOLE_API="http://localhost/api"
PIHOLE_PASSWORD="${PIHOLE_PASSWORD:-your-pihole-password}"  # Set via environment or replace
BLOCKED_GROUP=1   # AppleTV_Blocked
ALLOWED_GROUP=0   # Default (erlaubt)

# Apple TV MACs
declare -A DEVICES=(
    # Replace with your real MAC addresses
    ["beamer"]="AA:BB:CC:DD:EE:01"
    ["lcd"]="AA:BB:CC:DD:EE:02"
    ["wohnzimmer"]="AA:BB:CC:DD:EE:03"
)

# Global SID variable (for session reuse and cleanup)
SID=""

cleanup() {
    if [ -n "$SID" ]; then
        curl -s "$PIHOLE_API/auth" -X DELETE -H "sid: $SID" > /dev/null 2>&1
    fi
}
trap cleanup EXIT

get_sid() {
    if [ -n "$SID" ]; then
        echo "$SID"
        return
    fi
    
    local response=$(curl -s "$PIHOLE_API/auth" -X POST \
        -d "{\"password\":\"$PIHOLE_PASSWORD\"}" \
        -H "Content-Type: application/json")
    
    # Check for error
    if echo "$response" | grep -q '"error"'; then
        local error=$(echo "$response" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('error',{}).get('message','Unknown error'))" 2>/dev/null)
        echo "❌ Pi-hole API Fehler: $error" >&2
        return 1
    fi
    
    SID=$(echo "$response" | python3 -c "import sys,json; print(json.load(sys.stdin)['session']['sid'])" 2>/dev/null)
    
    if [ -z "$SID" ]; then
        echo "❌ Konnte keine Session erstellen" >&2
        return 1
    fi
    
    echo "$SID"
}

set_group() {
    local mac=$1
    local group=$2
    local sid=$(get_sid)
    
    if [ -z "$sid" ] || [[ "$sid" == "❌"* ]]; then
        return 1
    fi
    
    curl -s -X PUT "$PIHOLE_API/clients/$mac" \
        -H "sid: $sid" \
        -H "Content-Type: application/json" \
        -d "{\"groups\":[$group]}" > /dev/null
}

get_status() {
    local mac=$1
    local sid=$(get_sid)
    
    if [ -z "$sid" ] || [[ "$sid" == "❌"* ]]; then
        echo "FEHLER"
        return 1
    fi
    
    curl -s "$PIHOLE_API/clients" -H "sid: $sid" | \
        python3 -c "
import sys, json
data = json.load(sys.stdin)
mac = '$mac'.upper()
for c in data.get('clients', []):
    if c['client'].upper() == mac:
        groups = c.get('groups', [])
        # Gruppe 1 = blocked, alles andere = erlaubt
        print('GESPERRT' if 1 in groups else 'ERLAUBT')
        sys.exit(0)
print('UNBEKANNT')
"
}

do_action() {
    local action=$1
    local device=$2
    local mac=${DEVICES[$device]}
    local name=$device
    
    if [ -z "$mac" ]; then
        echo "❌ Unbekanntes Gerät: $device"
        return 1
    fi
    
    case "$action" in
        block)
            set_group "$mac" $BLOCKED_GROUP
            echo "🚫 $name GESPERRT"
            ;;
        allow)
            set_group "$mac" $ALLOWED_GROUP
            echo "✅ $name ERLAUBT"
            ;;
        status)
            local status=$(get_status "$mac")
            if [ "$status" = "GESPERRT" ]; then
                echo "🚫 $name: GESPERRT"
            elif [ "$status" = "ERLAUBT" ]; then
                echo "✅ $name: ERLAUBT"
            else
                echo "⚠️ $name: $status"
            fi
            ;;
        *)
            echo "Usage: $0 [block|allow|status] [all|beamer|lcd|wohnzimmer]"
            return 1
            ;;
    esac
}

# Main
ACTION=$1
TARGET=$2

if [ -z "$ACTION" ]; then
    echo "Usage: $0 [block|allow|status] [all|beamer|lcd|wohnzimmer]"
    exit 1
fi

if [ "$TARGET" = "all" ] || [ -z "$TARGET" ]; then
    for device in beamer lcd wohnzimmer; do
        do_action "$ACTION" "$device"
    done
else
    do_action "$ACTION" "$TARGET"
fi
