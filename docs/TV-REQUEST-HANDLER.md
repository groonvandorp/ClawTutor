# TV-Request Handler (für main-Agent)

## Wenn ein Tutor-Agent eine SCREENTIME_BALANCE Anfrage schickt

Format: `SCREENTIME_BALANCE: <kind>`

**Ausführen:**
```bash
python3 scripts/screentime-db.py balance <kind>
```

**Antwort:** "💰 <Kind>: X Minuten"

---

## Wenn ein Tutor-Agent eine SCREENTIME_ADD schickt

Format: `SCREENTIME_ADD: <kind> <minuten> "<grund>"`

**Ausführen:**
```bash
python3 scripts/screentime-db.py add <kind> <minuten> "<grund>"
```

**Antwort:** "✅ +X Min für <Kind>. Neues Guthaben: Y Min"

---

## Wenn ein Tutor-Agent eine TV_REQUEST schickt

Format: `TV_REQUEST: <kind> möchte <tv> für <minuten> Minuten`

### Vorgehen:

1. **Parse die Anfrage:**
   - Kind: olivia / arthur
   - TV: beamer / lcd / wohnzimmer
   - Minuten: Zahl

2. **Führe aus:**
```bash
./scripts/tv-session.sh start <kind> <tv> <minuten>
```

3. **Antworte dem Tutor:**
   - Bei Erfolg: "✅ <TV> freigeschaltet für <X> Min. Endet um <Uhrzeit>."
   - Bei Fehler: "❌ <Fehlermeldung>"

### Beispiel:

**Eingehend:** "TV_REQUEST: arthur möchte beamer für 20 Minuten"

**Ausführen:**
```bash
./scripts/tv-session.sh start arthur beamer 20
```

**Antwort bei Erfolg:**
"✅ Beamer freigeschaltet für 20 Min. Endet um 18:45. Session-ID: 3"

**Antwort bei Fehler:**
"❌ Nur 10 Min Guthaben verfügbar, 20 angefragt."

## Wichtig

- Der Auto-Off Cron läuft alle 2 Minuten
- Bei manueller Abschaltung: `./scripts/tv-session.sh end <session_id>`
- Guthaben prüfen: `python3 scripts/screentime-db.py balance <kind>`
