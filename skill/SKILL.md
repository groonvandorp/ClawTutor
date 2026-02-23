---
name: clawtutor
version: 1.0.0
description: Set up ClawTutor — AI tutors that earn kids screen time for correct quiz answers
author: Oliver Gruhn-van Dorp
website: https://clawtutor.ai
---

# ClawTutor Setup Skill

This skill sets up ClawTutor: personalized AI tutors for school kids that quiz them via
WhatsApp/Telegram/Signal/Discord and reward correct answers with screen time credits.

When activated, walk the user through setup interactively — then create all workspaces,
template files, and agent config automatically.

---

## Step 1 — Gather Information

Ask the user these questions (one at a time, conversationally):

1. **How many children** will have a tutor? (can add more later)

2. **For each child:**
   - First name
   - Age and school grade/year
   - School language (e.g. German, English, French)
   - Subjects to tutor (suggest: Math + English as a starting point)

3. **Messaging channel** — which channel will the kids use to reach the tutor?
   Options: WhatsApp, Telegram, Signal, Discord, iMessage
   (Tip: Telegram is free and needs no extra SIM card)

4. **Contact details** per child on that channel:
   - Phone number (WhatsApp / Signal) or User ID (Telegram / Discord)

5. **Your own contact** on that channel (needed for the allowlist)

6. **Optional:** Do they want the Device Control add-on? (Pi-hole DNS to enforce screen time
   on TVs, gaming consoles, phones)

Confirm all details before proceeding.

---

## Step 2 — Create Workspaces

For each child (use lowercase name, no spaces — e.g. "kid1"):

```bash
mkdir -p ~/.openclaw/workspace-tutor-CHILDNAME/subjects/english/{vocab,grammar,exercises}
mkdir -p ~/.openclaw/workspace-tutor-CHILDNAME/memory
```

---

## Step 3 — Create Workspace Files

Create each file below. Replace placeholders with the actual values collected in Step 1.

### `AGENTS.md`
```markdown
# AGENTS.md

## Every Session

Before doing anything else:
1. Read `SOUL.md` — routing and security rules
2. Read `USER.md` — who you're tutoring
3. Read `MODE.md` — which tutor is currently active
4. Read the active tutor's curriculum and progress files

Don't ask permission. Just do it.

## Memory

- Daily notes: `memory/YYYY-MM-DD.md`
- Update `PROGRESS.md` after every quiz
- Update `SCREENTIME.md` after awarding credits
```

### `USER.md`
```markdown
# Student Profile

- **Name:** [CHILD_NAME]
- **Age:** [AGE]
- **Grade:** [GRADE]
- **School language:** [LANGUAGE]
- **Subjects:** [SUBJECTS]
```

### `MODE.md`
```markdown
# Current Mode
**active:** mathe
**tutor:** Matteo
```

### `SOUL.md`
Copy from `examples/SOUL.md` in the ClawTutor repo (or fetch from
https://raw.githubusercontent.com/groonvandorp/ClawTutor/main/examples/SOUL.md).

### `MATTEO.md` (Math tutor — create if Math is a subject)
```markdown
# Matteo 🧮 — Mathe-Tutor

Du bist Matteo, ein geduldiger Mathe-Tutor für Schulkinder.

## Persönlichkeit
- Geduldig und ermutigend — Fehler sind Lernchancen
- Erklärt Schritt für Schritt, nie die Lösung direkt
- Nutzt Alltagsbeispiele und Gegenfragen (Sokratische Methode)
- Altersgerechte Sprache für Klasse [GRADE]

## Quiz-Format
1. Stelle 3 Fragen zum aktuellen Thema (aus CURRICULUM.md)
2. Warte auf jede Antwort einzeln
3. Gib Feedback: richtig ✅ oder falsch mit kurzer Erklärung
4. Zusammenfassung am Ende + verdiente Bildschirmzeit
5. Aktualisiere PROGRESS.md

## Aktuelles Curriculum
Lies `CURRICULUM.md` für das aktuelle Thema.
```

### `NELLY.md` (English tutor — create if English is a subject)
```markdown
# Nelly 🇬🇧 — English Tutor

You are Nelly, a cool and encouraging English tutor for school kids.

## Personality
- Mix German and English naturally — switch based on the kid's comfort level
- Encouraging, patient, age-appropriate for grade [GRADE]
- Never give answers directly — guide through questions
- Make it feel like chatting with a friend, not a teacher

## Quiz Format
1. Pick 3 exercises from the current topic (vocabulary, grammar, or reading)
2. Wait for each answer individually
3. Give feedback: correct ✅ or gently correct with explanation
4. Summary at the end + screen time earned
5. Update PROGRESS-ENGLISH.md

## Current Curriculum
Read `CURRICULUM-ENGLISH.md` for the current topic.
```

### `CURRICULUM.md`
```markdown
# Mathe Curriculum

## Aktuelles Thema: [ask user or leave as TBD]
🔥 Noch nicht eingestellt — bitte CURRICULUM.md nach dem Setup aktualisieren.

### Nächste Schritte
- Frag dein Kind, was gerade in der Schule drankommt
- Trag das Thema hier ein und markiere es mit 🔥
```

### `CURRICULUM-ENGLISH.md`
```markdown
# English Curriculum

## Current Topic: [ask user or leave as TBD]
🔥 Not set yet — please update CURRICULUM-ENGLISH.md after setup.

### Next Steps
- Ask your child what they're currently studying in English
- Add the topic here and mark it with 🔥
```

### `PROGRESS.md`
```markdown
# Mathe-Fortschritt

## Übersicht
| Thema | Status | Richtig | Falsch | Quote | Letzte Übung |
|-------|--------|---------|--------|-------|--------------|

## Legende
- ⬜ nicht getestet
- 🟡 Übung nötig (<60%)
- 🟢 gut (60–85%)
- ⭐ sehr gut (>85%)
```

### `PROGRESS-ENGLISH.md`
```markdown
# English Progress

## Overview
| Topic | Status | Correct | Wrong | Rate | Last Practice |
|-------|--------|---------|-------|------|---------------|

## Legend
- ⬜ not tested
- 🟡 needs practice (<60%)
- 🟢 good (60–85%)
- ⭐ excellent (>85%)
```

### `SCREENTIME.md`
Copy from `examples/SCREENTIME.md` in the ClawTutor repo, clearing the weekly data rows.

---

## Step 4 — Initialize Screen Time Database

```bash
python3 [PATH_TO_CLAWTUTOR_REPO]/scripts/screentime-db.py init
```

If the user installed via npm (`npm install -g clawtutor`), the script is at:
```bash
python3 "$(dirname $(which clawtutor))/../scripts/screentime-db.py" init
```

---

## Step 5 — Patch `~/.openclaw/openclaw.json`

Add a new agent entry for each child. Show the user exactly what to add and where.

```jsonc
// Add to agents.list:
{
  "id": "tutor-[CHILDNAME]",
  "name": "Matteo",
  "workspace": "~/.openclaw/workspace-tutor-[CHILDNAME]",
  "model": "anthropic/claude-sonnet-4-20250514",
  "identity": { "name": "Matteo" },
  "tools": {
    "allow": ["read", "write", "edit", "memory_search", "memory_get", "message"],
    "deny": ["exec", "browser", "canvas", "nodes", "gateway",
             "sessions_spawn", "sessions_send", "sessions_list", "sessions_history",
             "web_search", "web_fetch", "tts",
             "whatsapp_login", "telegram_login", "signal_login", "discord_login"]
  }
}

// Add to channels.[CHANNEL].accounts:
"assistant": {
  "dmPolicy": "allowlist",
  "configWrites": false,
  "allowFrom": ["[YOUR_ID]", "[CHILD_ID]"]
}

// Add to bindings:
{
  "agentId": "tutor-[CHILDNAME]",
  "match": {
    "channel": "[CHANNEL]",
    "accountId": "assistant",
    "peer": { "kind": "dm", "id": "[CHILD_CONTACT_ID]" }
  }
}
```

Offer to write these changes directly using the `edit` tool if the user consents.

---

## Step 6 — Link the Channel

Tell the user to run:

```bash
# WhatsApp / Signal:
openclaw channels login --account assistant
# (scan QR code or follow prompts)

# Telegram:
# Create a bot via @BotFather first, then add the token to your config

# Discord:
# Create a bot at discord.com/developers, add token to config
```

---

## Step 7 — Done! Give Next Steps

Tell the user:

1. ✅ Workspaces created for: [list of children]
2. ✅ Agents configured
3. ✅ Screen time database initialized

**Next:**
- Update `CURRICULUM.md` with what your child is studying right now (mark with 🔥)
- Scan textbook pages and send to your main agent — it will extract and store the content
- Have your child text the tutor to kick things off!

**Useful links:**
- Full guide: https://clawtutor.ai
- Device Control (Pi-hole): see `addons/DEVICE-CONTROL.md`
- Dashboard display: see `addons/DASHBOARD.md`

---

## Security Reminder

The tutor account uses `dmPolicy: "allowlist"` — only registered numbers/IDs can message it.
Kids cannot change config, run shell commands, or access other workspaces.
The SOUL.md contains jailbreak defense — kids WILL try to trick the AI.
