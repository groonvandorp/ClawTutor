# 🐾 ClawTutor

### AI-Powered Tutoring System built on OpenClaw

A complete guide to building a personalized AI tutoring system for school kids using OpenClaw on a Raspberry Pi. The tutors quiz your kids via WhatsApp, track progress, and reward screen time for correct answers.

---

## What You Get

- **Multiple AI tutors** with distinct personalities (e.g. "Matteo" for Math, "Nelly" for English)
- **Per-child agents** — each kid gets their own tutor session, tailored to their grade level
- **WhatsApp integration** — kids text the tutor on a dedicated number
- **Subject switching** — kids type `/mathe` or `/english` (or the tutor's name) to switch subjects
- **Curriculum-aware** — tutors know the school textbook, current topics, and upcoming exams
- **Progress tracking** — automatic scoring per topic with visual status (🟡🟢⭐)
- **Screen time rewards** — earn minutes of screen time for correct answers
- **Prompt injection protection** — kids can't trick the AI into breaking its rules
- **Automated backups** — daily to local disk + USB stick

## Hardware

- **Raspberry Pi 5** (4GB+ RAM recommended)
- Raspberry Pi OS (64-bit)
- USB stick for backups (optional)
- A spare phone number for the tutor's WhatsApp (dedicated SIM or eSIM)
- A phone to register WhatsApp on that number (can be WhatsApp Business on your existing phone)

**Cost:** ~€80 for the Pi + ~€5/month for a prepaid SIM + Anthropic API usage (~€5-15/month depending on usage)

## Architecture

```
┌─────────────────────────────────────────────────┐
│                 Raspberry Pi                     │
│                                                  │
│  ┌──────────────────────────────────────────┐   │
│  │           OpenClaw Gateway                │   │
│  │                                           │   │
│  │  ┌─────────┐  ┌─────────┐  ┌──────────┐ │   │
│  │  │  Main   │  │  Tutor  │  │  Tutor   │ │   │
│  │  │  Agent  │  │ (Kid 1) │  │ (Kid 2)  │ │   │
│  │  └─────────┘  └─────────┘  └──────────┘ │   │
│  │                                           │   │
│  │  WhatsApp Account 1    WhatsApp Account 2 │   │
│  │  (your personal)       (tutor number)     │   │
│  └──────────────────────────────────────────┘   │
│                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐  │
│  │Workspace │  │Workspace │  │  Workspace   │  │
│  │  (main)  │  │ (kid 1)  │  │  (kid 2)     │  │
│  └──────────┘  └──────────┘  └──────────────┘  │
└─────────────────────────────────────────────────┘

Parent texts ──→ WhatsApp Account 1 ──→ Main Agent
Kid 1 texts  ──→ WhatsApp Account 2 ──→ Tutor Agent (Kid 1)
Kid 2 texts  ──→ WhatsApp Account 2 ──→ Tutor Agent (Kid 2)
```

## Step-by-Step Setup

### 1. Install OpenClaw on Raspberry Pi

```bash
# Install Node.js 22+
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo bash -
sudo apt install -y nodejs

# Install OpenClaw
npm install -g openclaw

# Run the setup wizard
openclaw onboard
```

The wizard will:
- Create your config at `~/.openclaw/openclaw.json`
- Set up your Anthropic API key
- Link your personal WhatsApp (QR scan)
- Create the main agent

### 2. Set Up the Gateway as a Service

```bash
openclaw service install
openclaw gateway start
```

**Important:** Add network dependency so the gateway waits for internet on boot:

Edit `~/.config/systemd/user/openclaw-gateway.service` and add before `ExecStart`:
```ini
ExecStartPre=/bin/sh -c 'until ping -c1 -W2 1.1.1.1 >/dev/null 2>&1; do sleep 2; done'
```

Then reload:
```bash
systemctl --user daemon-reload
```

### 3. Create Tutor Workspaces

Each child gets their own workspace with curriculum, progress tracking, and tutor personality files.

```bash
mkdir -p ~/.openclaw/workspace-tutor-CHILDNAME
mkdir -p ~/.openclaw/workspace-tutor-CHILDNAME/subjects/english/{vocab,grammar,exercises}
mkdir -p ~/.openclaw/workspace-tutor-CHILDNAME/memory
```

### 4. Create Workspace Files

Each workspace needs these files:

#### `SOUL.md` — The Router
Controls which tutor personality is active and handles switching between subjects. Contains:
- Switching logic (`/mathe`, `/english`, tutor names)
- Security rules (prompt injection defense)
- Screen time reward system
- Exam preparation mode
- WhatsApp formatting rules

#### `MATTEO.md` / `NELLY.md` — Tutor Personalities
Each subject tutor gets a personality file defining:
- Name and emoji
- Personality traits (patient, encouraging, age-appropriate)
- Teaching style (step-by-step, examples, no solutions)
- Language (German for explanations, target language for practice)
- Quiz format and exercise types

#### `MODE.md` — Current Active Tutor
Simple file tracking which tutor is active:
```markdown
# Current Mode
**active:** mathe
**tutor:** Matteo
```

#### `CURRICULUM.md` / `CURRICULUM-ENGLISH.md` — What to Teach
Based on the actual school textbook table of contents:
- Textbook info (title, ISBN, publisher)
- Chapter-by-chapter structure with page numbers
- Current topic marked with 🔥
- Upcoming exam dates and preparation plans

#### `PROGRESS.md` / `PROGRESS-ENGLISH.md` — Learning Progress
Automatic tracking per topic:
```markdown
| Topic | Status | Correct | Wrong | Rate | Last Practice |
|-------|--------|---------|-------|------|--------------|
| Fractions | 🟢 good | 8 | 2 | 80% | 2026-01-30 |
```

#### `SCREENTIME.md` — Screen Time Rewards
Motivational reward system:
- ✅ Correct answer in quiz = 10 min
- 🔥 3/3 perfect = bonus 10 min (total 40)
- 📈 5-day streak = extra 30 min for the weekend
- 💪 Voluntary practice = 5 min per correct answer

#### `USER.md` — Child's Info
```markdown
- **Name:** ...
- **Age:** ...
- **School:** Grade X, Gymnasium in City (State)
- **Curriculum:** State curriculum
- **Language:** German
```

#### `AGENTS.md` — Agent Instructions
Tells the agent which files to read on startup and how to handle sessions.

### 5. Add Textbook Content

Scan your child's textbook pages (table of contents, vocab lists, grammar sections) and send them to your main agent. It will:
1. Extract text via vision model
2. Convert to structured markdown
3. Store in the workspace's `subjects/` folder

### 6. Configure Agents

Add tutor agents to `openclaw.json`:

```json5
{
  agents: {
    list: [
      { id: "main", default: true, workspace: "~/.openclaw/workspace" },
      {
        id: "tutor-childname",
        name: "Matteo",
        workspace: "~/.openclaw/workspace-tutor-childname",
        model: "anthropic/claude-sonnet-4-20250514",  // good enough, cheaper
        identity: { name: "Matteo" },
        tools: {
          allow: ["read", "write", "edit", "memory_search", "memory_get", "message"],
          deny: ["exec", "browser", "canvas", "nodes", "gateway",
                 "sessions_spawn", "sessions_send", "sessions_list",
                 "sessions_history", "web_search", "web_fetch", "tts",
                 "whatsapp_login"]
        }
      }
    ]
  }
}
```

**Key points:**
- Use `claude-sonnet-4` — cheaper than Sonnet 4.5/Opus, plenty smart for school tutoring
- Restrict tools — tutors only need read/write/edit for their workspace files + message for WhatsApp
- Each child gets a separate agent ID and workspace

### 7. Set Up Dedicated WhatsApp Number

Register a second phone number on WhatsApp (WhatsApp Business on your existing phone works great).

Add the second account to config:
```json5
{
  channels: {
    whatsapp: {
      accounts: {
        default: {},  // your personal number
        assistant: {  // tutor number
          dmPolicy: "allowlist",
          configWrites: false,  // kids can't change config
          allowFrom: [
            "+49YOUR_NUMBER",
            "+49CHILD1_NUMBER",
            "+49CHILD2_NUMBER"
          ]
        }
      }
    }
  }
}
```

Link the second account:
```bash
openclaw channels login --account assistant
# Scan QR with the tutor phone's WhatsApp
```

### 8. Bind Children to Their Agents

Route each child's messages to their tutor agent:

```json5
{
  bindings: [
    {
      agentId: "tutor-child1",
      match: {
        channel: "whatsapp",
        accountId: "assistant",
        peer: { kind: "dm", id: "+49CHILD1_NUMBER" }
      }
    },
    {
      agentId: "tutor-child2",
      match: {
        channel: "whatsapp",
        accountId: "assistant",
        peer: { kind: "dm", id: "+49CHILD2_NUMBER" }
      }
    }
  ]
}
```

### 9. Security Hardening

The tutor number should be locked down:

**Already secure by default:**
- `commands.config: false` — no config changes via chat
- `commands.bash: false` — no shell access
- `commands.restart: false` — no gateway restart
- `commands.debug: false` — no debug mode

**Additional:**
- `configWrites: false` on the assistant account
- Tool restrictions in agent config (no exec, browser, gateway tools)
- Prompt injection defense in SOUL.md
- File access restricted to specific allowed files

**Still available (harmless):**
- `/reset` — clears chat session
- `/status` — shows session info

### 10. Automated Backups

Create a backup script at `~/backup-openclaw.sh`:

```bash
#!/bin/bash
BACKUP_DIR="$HOME/backups/openclaw"
MAX_LOCAL=7

mkdir -p "$BACKUP_DIR"
FILENAME="openclaw-backup-$(date +%Y%m%d-%H%M).tar.gz"
tar czf "$BACKUP_DIR/$FILENAME" -C "$HOME" .openclaw/ 2>/dev/null

# Rotate local backups
ls -1t "$BACKUP_DIR"/openclaw-backup-*.tar.gz | tail -n +$((MAX_LOCAL + 1)) | xargs rm -f 2>/dev/null

# Copy to USB if mounted
USB_MOUNT="/mnt/backup"
if mountpoint -q "$USB_MOUNT" 2>/dev/null; then
    cp "$BACKUP_DIR/$FILENAME" "$USB_MOUNT/"
    ls -1t "$USB_MOUNT"/openclaw-backup-*.tar.gz | tail -n +31 | xargs rm -f 2>/dev/null
fi
```

Add to crontab (daily at 3 AM):
```bash
chmod +x ~/backup-openclaw.sh
(crontab -l; echo "0 3 * * * ~/backup-openclaw.sh >> ~/backups/backup.log 2>&1") | crontab -
```

Optional: format a USB stick as FAT32 labeled "BACKUP" and add to `/etc/fstab`:
```
UUID=XXXX-XXXX /mnt/backup vfat defaults,nofail,uid=1000,gid=1000 0 0
```

## How It Works (Kid's Perspective)

1. Kid saves the tutor number as a contact (e.g. "Matteo 🧮")
2. Kid texts "Hallo" → Matteo introduces himself
3. Matteo asks what they're working on in class
4. Kid can ask for help, get explanations, or request a quiz
5. After a quiz, Matteo tells them how much screen time they earned
6. Kid types `/english` → Nelly takes over for English practice
7. Kid types `/mathe` → back to Matteo

## Tips

- **Scan the textbook TOC first** — gives the tutor the full course structure
- **Update CURRICULUM.md** when topics change in class — mark current with 🔥
- **Add exam dates** — tutors switch to preparation mode automatically
- **Screen time is motivating** — kids actually want to do quizzes to earn minutes
- **Use a cheaper model** — Claude Sonnet 4 is plenty for K-12 tutoring
- **Keep it fun** — the tutor personalities make it feel less like homework
- **Prompt injection is real** — kids WILL try to jailbreak the tutor, the SOUL.md rules handle it

## Cost Estimate

| Item | Cost |
|------|------|
| Raspberry Pi 5 (4GB) | ~€80 one-time |
| Prepaid SIM | ~€5/month |
| Anthropic API (Sonnet 4, moderate use) | ~€5-15/month |
| **Total monthly** | **~€10-20/month** |

Compare that to human tutoring at €30-50/hour. 😉

## File Structure

```
~/.openclaw/
├── openclaw.json              # Main config
├── credentials/               # WhatsApp auth (don't share!)
├── workspace/                 # Main agent workspace
├── workspace-tutor-child1/    # Child 1's tutor workspace
│   ├── SOUL.md               # Tutor router + security
│   ├── MATTEO.md             # Math tutor personality
│   ├── NELLY.md              # English tutor personality
│   ├── MODE.md               # Active tutor
│   ├── AGENTS.md             # Agent instructions
│   ├── USER.md               # Child info
│   ├── CURRICULUM.md         # Math curriculum + textbook
│   ├── CURRICULUM-ENGLISH.md # English curriculum + textbook
│   ├── PROGRESS.md           # Math progress tracking
│   ├── PROGRESS-ENGLISH.md   # English progress tracking
│   ├── SCREENTIME.md         # Screen time rewards
│   ├── LEHRPLAN-NRW-7.md     # Official state curriculum
│   ├── subjects/english/     # Scanned textbook material
│   │   ├── vocab/
│   │   ├── grammar/
│   │   └── exercises/
│   └── memory/               # Session memory
└── workspace-tutor-child2/    # Child 2 (same structure)
```

## FAQ

**Can I add more subjects?**
Yes! Create a new personality file (e.g. `FRANZ.md` for French), add a curriculum file, update SOUL.md with the switching logic.

**Can I add more children?**
Yes! Create a new agent + workspace, add their number to the allowlist and bindings.

**What if WhatsApp disconnects?**
The gateway auto-reconnects. If you started without network, restart the gateway.

**Can kids change the model to something expensive?**
They could use `/model` — to prevent this, the tutor's SOUL.md instructs it to only respond to subject-related input. You could also monitor usage via `/status`.

**Does it work with other messengers?**
Yes! OpenClaw supports Telegram, Signal, Discord, and more. Telegram is a good alternative to keep tutoring separate from WhatsApp social life.

**Can the tutor send images/diagrams?**
The tutor describes things in text (WhatsApp-optimized). For geometry, it describes constructions step by step. Image generation could be added with additional tools.

---

*🐾 ClawTutor — built with [OpenClaw](https://github.com/openclaw/openclaw)*
*Docs: https://docs.openclaw.ai | Community: https://discord.com/invite/clawd | Skills: https://clawdhub.com*
