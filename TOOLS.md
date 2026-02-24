# TOOLS.md - Local Notes

Skills define *how* tools work. This file is for *your* specifics — the stuff that's unique to your setup.

## TV-Steuerung (via Pi-hole)

### Manuelle Steuerung (Eltern/Owner)
Direkte Befehle ohne Guthaben-Abzug, läuft unbegrenzt:

- `tv an` → Alle TVs erlauben
- `tv aus` → Alle TVs sperren
- `tv status` → Status anzeigen
- `tv wohnzimmer an`, `wohnzimmer an`, `beamer aus`, `lcd status` → Einzeln steuern

Script: `addons/device-control/device-control.sh [block|allow|status] [all|beamer|lcd|wohnzimmer]`

### Session-Steuerung (Kinder)
Mit Guthaben und Auto-Off:

- `30 min tv wohnzimmer für kid1` → Prüft Guthaben, bucht ab, startet Session mit Timer
- Auto-Off nach Ablauf (Cron alle 2 Min prüft abgelaufene Sessions)

**Example devices:**
| Name | MAC |
|------|-----|
| beamer | AA:BB:CC:DD:EE:01 |
| lcd | AA:BB:CC:DD:EE:02 |
| wohnzimmer | AA:BB:CC:DD:EE:03 |

Pi-hole Web: `http://YOUR_PI_IP/admin` (set password via `pihole -a -p`)

## What Goes Here

Things like:
- Camera names and locations
- SSH hosts and aliases  
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.
