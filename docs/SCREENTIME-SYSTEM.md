# Bildschirmzeit-System

## Übersicht

Kinder verdienen durch Quizze Bildschirmzeit, die sie für TV-Sessions einlösen können.

## Für Tutoren: Zeit gutschreiben

Nach einem Quiz mit richtigen Antworten:

```bash
# Zeit gutschreiben
python3 scripts/screentime-db.py add <kind> <minuten> "<grund>"

# Beispiele:
python3 scripts/screentime-db.py add olivia 30 "Quiz 12.02: 3/3 richtig"
python3 scripts/screentime-db.py add arthur 20 "Quiz 12.02: 2/3 richtig"
```

## Für Kinder: TV freischalten

Ein Kind kann im Chat schreiben:
- "Beamer 30 Minuten"
- "LCD 20 Min"  
- "Wohnzimmer 45 min"

Der Tutor/Agent prüft das Guthaben und schaltet ggf. frei.

### Intern (Agent-Befehle):

```bash
# Guthaben prüfen
python3 scripts/screentime-db.py balance olivia

# TV-Session starten (prüft Guthaben, zieht ab, schaltet TV frei)
./addons/device-control/tv-session.sh start olivia beamer 30

# Session manuell beenden
./addons/device-control/tv-session.sh end <session_id>

# Abgelaufene Sessions prüfen und TVs sperren
./addons/device-control/tv-session.sh check
```

## Guthaben-Regeln

| Ergebnis | Minuten |
|----------|---------|
| Richtige Antwort | +10 Min |
| Streak-Bonus (3 Tage) | +5 Min |
| Streak-Bonus (7 Tage) | +10 Min |
| Freiwillige Übung | +5 Min |

## Datenbank

Pfad: `data/screentime.db`

Tabellen:
- `budget` — aktuelles Guthaben pro Kind
- `transactions` — Historie aller Gutschriften/Abbuchungen
- `tv_sessions` — aktive und beendete TV-Sessions

## Flow

```
Kind verdient Zeit (Quiz)
        ↓
Tutor: screentime-db.py add
        ↓
Kind fragt: "Beamer 30 min"
        ↓
Agent prüft Guthaben
        ↓
    ┌───┴───┐
    ↓       ↓
  Genug   Nicht genug
    ↓       ↓
  TV an   "Sorry, nur X Min"
    ↓
  Cron: Auto-Off nach X Min
    ↓
  TV aus
```

## Cron-Job für Auto-Off

Es sollte regelmäßig geprüft werden, ob Sessions abgelaufen sind:

```bash
# Alle 5 Minuten prüfen
*/5 * * * * /home/jarvis/.openclaw/workspace/addons/device-control/tv-session.sh check
```

Oder als OpenClaw Cron-Job mit `kind: systemEvent`.

## TVs

| Name | Beschreibung |
|------|-------------|
| beamer | Beamer im Wohnzimmer |
| lcd | LCD TV (Wohnzimmer) |
| wohnzimmer | TV Wohnzimmer |
