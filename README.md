<p align="center">
  <img src="docs/clawtutor-mascot.png" alt="ClawTutor" height="180" />
</p>

<h1 align="center">ClawTutor</h1>
<p align="center">
  <strong>Turn screen time into learn time.</strong><br>
  <em>Screen time conflict. Outsourced.</em>
</p>



AI tutors that quiz your kids via WhatsApp, Telegram, Signal, Discord, or any channel OpenClaw supports — and reward correct answers with screen time credits.

🌐 [clawtutor.ai](https://clawtutor.ai) · 📦 [GitHub](https://github.com/groonvandorp/ClawTutor) · 🏠 [Real setup](https://clawtutor.ai/olivers-setup.html) · 📝 [Blog](https://clawtutor.ai/blog.html) · 📧 [Contact](https://clawtutor.ai/contact.html) · 📸 [Instagram](https://instagram.com/clawtutor) · ▶️ [YouTube](https://www.youtube.com/@ClawTutor)

> *Built by a father who was tired of the daily screen time negotiations with his two kids.*

---

## 📖 The Story

**The Problem:** Like many parents, I was caught in an endless negotiation loop. *"Can I watch TV?" "Did you do your homework?" "But I already did math yesterday!"* The struggle was real — and exhausting.

**The Insight:** Kids are motivated by screen time. What if we could channel that motivation into learning? Instead of limiting screen time as punishment, what if they could *earn* it?

**The Solution:** ClawTutor — AI tutors running on a Raspberry Pi that:
- Quiz the kids via WhatsApp, Telegram, Signal, or Discord — wherever they already are
- Reward correct answers with screen time credits
- Actually make them *want* to study (yes, really)
- Track progress automatically per topic

**The Result:** My kids now text their tutors voluntarily. They compete for streaks. They ask for extra quizzes. The screen time war is over — and learning won.

---

## ✨ Features

### Core System
| Feature | Description |
|---------|-------------|
| 🎓 **AI Tutors** | Personalized tutors per subject (Math, English, Music — and more coming) |
| 💬 **Any Messenger** | WhatsApp, Telegram, Signal, Discord — kids text the tutor like a friend |
| 💰 **Screen Time Credits** | Earn minutes for correct answers, tracked in a balance |
| 📊 **Progress Tracking** | Automatic per-topic scoring (🟡→🟢→⭐) |
| 🔥 **Streak System** | Bonus minutes for consecutive days of practice |
| 🛡️ **Jailbreak Proof** | Prompt injection defense — kids can't trick the AI |
| 👨‍👩‍👧‍👦 **Multi-Child** | Each kid gets their own tutor agent and workspace |
| 📚 **Curriculum-Aware** | Tutors know the textbook, current chapter, and weak spots |
| 📅 **Exam Prep Mode** | Countdown to tests, intensified practice, topic-focused review |
| 🌍 **Multilingual** | Full German and English templates included; extensible to any language |
| 📲 **iOS App** | Native app as an alternative messenger (optional) |

### Optional Add-ons
| Add-on | Description |
|--------|-------------|
| 🔒 **[Device Control](addons/DEVICE-CONTROL.md)** | Enforce screen time via Pi-hole DNS blocking |
| 🖥️ **[Dashboard](addons/DASHBOARD.md)** | Physical status display on SPI screen |

**Device Control supports any device whose DNS points at Pi-hole:**
- 📺 Streaming boxes (Apple TV, Fire TV, Chromecast, Android TV, Roku)
- 🎮 Gaming consoles (PlayStation, Xbox, Nintendo Switch) — WiFi or wired
- 📱 Phones & tablets — blocked on home WiFi
- 💻 Computers (laptops, PCs)
- 🔌 Smart plugs & home automation (Home Assistant, Shelly, TP-Link Kasa, IKEA Trådfri) — cuts power for offline/local games that bypass DNS

---

## 👥 Use Cases

ClawTutor isn't just for parents. Anyone who wants to gamify learning and control their own screen time:

| Who | Use Case |
|-----|----------|
| 👨‍👩‍👧‍👦 **Parents** | Manage kids' screen time while making them *want* to study |
| 🎓 **Students** | Self-discipline: "Netflix unlocks after 2 hours of studying" |
| 🧠 **ADHD & Focus** | Gamification to beat procrastination — earn your dopamine |
| 💼 **Remote Workers** | Block distracting sites until deep work goals are met |
| 💪 **Self-Improvers** | Learn languages, skills, anything — reward yourself with guilt-free breaks |

### Self-Tutoring Mode

Don't have kids? Use it on yourself:
- Set up a tutor for your learning goals (language, coding, certifications)
- Quiz yourself or let the AI quiz you
- Earn credits toward your own devices
- Block your own PlayStation until you've done your Duolingo 😅

---

## 💰 The Economics

| Item | Cost |
|------|------|
| [Raspberry Pi 5](https://www.raspberrypi.com/products/raspberry-pi-5/) 4 GB+ | ~€80 (one-time) |
| SIM for tutor number | pay-per-use / ~€1–5/month — only needed to register the number |
| Anthropic API (Claude Sonnet) | ~€5-15/month |
| **Monthly total** | **~€10-20** |

*Compare to human tutoring at €30-50/hour* 😉

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Raspberry Pi 5                          │
│                                                             │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                  OpenClaw Gateway                      │ │
│  │                                                        │ │
│  │   ┌─────────┐    ┌─────────┐    ┌─────────┐            │ │
│  │   │  Main   │    │  Tutor  │    │  Tutor  │            │ │
│  │   │ (Parent)│    │ (Kid 1) │    │ (Kid 2) │            │ │
│  │   │Opus 4.5 │    │Sonnet 4 │    │Sonnet 4 │            │ │
│  │   └────┬────┘    └────┬────┘    └────┬────┘            │ │
│  │        │              │              │                 │ │
│  │   WhatsApp 1     WhatsApp 2     WhatsApp 2             │ │
│  │   (personal)     (tutor)        (tutor)                │ │
│  └────────────────────────────────────────────────────────┘ │
│                              │                              │
│                    ┌─────────┴─────────┐                    │
│                    │  SQLite Database  │                    │
│                    │  (screen time     │                    │
│                    │   credits)        │                    │
│                    └───────────────────┘                    │
└─────────────────────────────────────────────────────────────┘
```

**How it works:**
1. Kid texts tutor on WhatsApp
2. Tutor quizzes them on current school topics
3. Correct answers → credits added to balance
4. Kid checks balance anytime ("How many credits do I have?")
5. Parent approves screen time based on balance

---

## 🎮 Screen Time Credit System

The secret sauce that makes kids *want* to study:

| Action | Reward |
|--------|--------|
| ✅ Correct quiz answer | +10 min |
| 🔥 Perfect 3/3 quiz | +40 min (30 + bonus) |
| 📈 5-day streak | +30 min weekend bonus |
| 💪 Voluntary practice | +5 min per answer |
| 🧹 Chore completed *(planned)* | configurable per task |

> **Planned — Chore Credits:** Kids will be able to earn screen time by completing household tasks (empty the dishwasher, brush teeth, clean their room, etc.). A parent confirms the chore via WhatsApp chat, and the credits are added instantly. Each chore maps to a configurable credit value.

Kids earn credits. How you "spend" them is up to you:
- **Manual:** Kid asks, you check balance, you decide
- **Honor system:** Kid manages their own screen time
- **Automated:** Use the [Device Control Add-on](addons/DEVICE-CONTROL.md) to enforce limits

---

## 📅 Exam Prep Mode

When a test is coming up, ClawTutor shifts into high gear:

### How It Works

1. **Register the exam** in `CALENDAR.md`:
   ```markdown
   ## Upcoming Exams
   - 2024-03-15: Math Test - Chapter 7 (Equations)
   - 2024-03-22: English Vocabulary Test
   ```

2. **Tutor activates countdown mode** (configurable: 14/7/3/1 days):
   - "📢 Maths test in 14 days — time for a first review!"
   - Increasing urgency as exam approaches
   - Focus shifts to exam-relevant topics

3. **Intensified practice:**
   - More questions on weak spots (tracked in `PROGRESS.md`)
   - Review of previously failed topics
   - Bonus credits for exam prep sessions

4. **Progress visibility:**
   - Topic mastery: 🔴 → 🟡 → 🟢 → ⭐
   - "You've got 3 out of 5 topics to green — 2 more to practise!"

### Example Flow

```
Tutor: "⚠️ Maths test in 3 days!
        Topic: Linear equations
        
        Your progress:
        ✅ Setting up equations — ⭐
        ✅ Solving equations — 🟢
        ⚠️ Word problems — 🟡
        ❌ Inequalities — 🔴
        
        Shall we practise word problems?"

Kid: "ok"

Tutor: "A train leaves at 8:00 am travelling at 120 km/h..."
```

### For Students (Self-Use)

Works the same for university exams, certifications, or any test:
- Add your exam dates
- Let the AI quiz you on weak areas
- Track your progress toward exam readiness
- Reward yourself with guilt-free breaks when you're prepared

---

## 📸 Screenshots

> *TODO: Add screenshots of WhatsApp chat and iOS app*

---

## 🚀 Quick Start

### Option A — npm (recommended)

One command installs ClawTutor and walks you through setup interactively:

```bash
# 1. Install OpenClaw (if not already)
npm install -g openclaw
openclaw onboard

# 2. Install ClawTutor and run the setup wizard
npm install -g clawtutor
clawtutor setup
```

The wizard asks for your children's names, grades, and messaging channel — then creates all workspaces, config, and the screen time database automatically.

### Option B — OpenClaw Skill (chat-based)

Already running OpenClaw? Install and run directly from chat with your main agent:

```
/skill install clawtutor
```

The tutor agent will walk you through setup conversationally — no terminal needed.

### Option C — Manual

```bash
npm install -g openclaw && openclaw onboard
git clone https://github.com/groonvandorp/ClawTutor.git
cat ClawTutor/SETUP.md
```

**Requirements:**
- [Raspberry Pi 5](https://www.raspberrypi.com/products/raspberry-pi-5/) with 4 GB+ RAM (or any Linux machine with Node.js 22+)
- [OpenClaw](https://github.com/openclaw/openclaw) installed
- [Anthropic API key](https://console.anthropic.com/)
- A messaging channel for the tutor (WhatsApp, Telegram, Signal, or Discord)

---

## 📂 Repository Structure

```
ClawTutor/
├── README.md              # You are here
├── SETUP.md               # Step-by-step installation guide
├── LICENSE                # License (free non-commercial, commercial requires permission)
│
├── cli/                   # npm package — `npm install -g clawtutor`
│   ├── package.json
│   ├── bin/clawtutor.js   # Interactive setup wizard (no external deps)
│   └── scripts/           # Scripts bundled with the npm package
│
├── skill/                 # OpenClaw skill — `/skill install clawtutor`
│   └── SKILL.md           # Chat-based setup for existing OpenClaw users
│
├── addons/                # Optional add-ons
│   ├── DEVICE-CONTROL.md  # Pi-hole device control (TVs, gaming, mobile, etc.)
│   └── DASHBOARD.md       # SPI status display
│
├── scripts/               # Shell scripts (source — also bundled in cli/)
│   ├── screentime-db.py   # Credit balance management
│   ├── appletv-access.sh  # (Add-on) Pi-hole device control
│   ├── tv-session.sh      # (Add-on) Session management
│   └── tv-auto-off.sh     # (Add-on) Cron auto-off
│
├── artwork/               # Logo and icon source files
│   └── *.png              # Originals from Gemini image generation
│
├── docs/                  # GitHub Pages website (clawtutor.ai)
│   ├── index.html         # Main landing page
│   ├── olivers-setup.html # Real-world setup walkthrough
│   ├── courses.html       # Available courses (Math, English, Music)
│   ├── contact.html       # Contact form (via Formsubmit)
│   ├── ecosystem.html     # Projects ClawTutor is built on
│   ├── blog.html          # Dev log & updates index
│   ├── blog/              # Individual blog posts
│   ├── icon.png           # App icon (transparent background)
│   └── logo.png           # Horizontal wordmark (transparent background)
│
├── examples/              # Example workspace files
│   ├── openclaw-example.jsonc   # Channel config (language-neutral)
│   ├── CALENDAR.md              # Exam tracking (language-neutral)
│   ├── de/                      # 🇩🇪 German examples
│   │   ├── SOUL.md
│   │   ├── CURRICULUM.md
│   │   ├── PROGRESS.md
│   │   └── SCREENTIME.md
│   └── en/                      # 🇬🇧 English examples
│       ├── SOUL.md
│       ├── CURRICULUM.md
│       ├── CURRICULUM-ENGLISH.md
│       ├── PROGRESS.md
│       └── SCREENTIME.md
│
└── dashboard/             # (Add-on) Mission Control display
    └── mission_control.py
```

---

## 📖 Documentation

| Document | Description |
|----------|-------------|
| [clawtutor.ai](https://clawtutor.ai) | Project website |
| [Courses](https://clawtutor.ai/courses.html) | Available courses: Math, English, Music — with roadmap |
| [Oliver's setup](https://clawtutor.ai/olivers-setup.html) | Real-world setup walkthrough (Raspberry Pi, WhatsApp, Apple TV, Nintendo Switch, PlayStation, Pi-hole) |
| [Contact](https://clawtutor.ai/contact.html) | Get in touch — oliver@clawtutor.ai |
| [Built on](https://clawtutor.ai/ecosystem.html) | All projects ClawTutor depends on |
| [Blog](https://clawtutor.ai/blog.html) | Dev log & upcoming changes — latest: [Gaming consoles under control](https://clawtutor.ai/blog/2026-02-21-gaming-consoles.html) |
| [SETUP.md](SETUP.md) | Complete installation guide |
| [addons/DEVICE-CONTROL.md](addons/DEVICE-CONTROL.md) | Optional: Control any device via Pi-hole DNS |
| [addons/DASHBOARD.md](addons/DASHBOARD.md) | Optional: Physical status display |
| [examples/](examples/) | Template files for workspaces |

---

## 🔒 Security

- **Isolated agents** — Each kid's tutor has no access to other workspaces
- **Tool restrictions** — Tutors can only read/write their curriculum files
- **No shell access** — Kids can't execute commands
- **Prompt injection defense** — SOUL.md contains jailbreak countermeasures
- **Allowlist** — Only registered phone numbers can chat with tutors

---

## ⚠️ Disclaimer & Requirements

> **ClawTutor is a self-hosted system. Running it safely requires solid IT and IT-security knowledge.**

### What you need to know before setting this up

This is not a plug-and-play consumer product. Operating ClawTutor responsibly requires:

- **Linux / Raspberry Pi OS** — comfortable with the terminal, SSH, systemd services, and file permissions
- **Networking basics** — understanding of DNS, firewall rules, local network configuration, and VPN (if you expose the gateway remotely)
- **IT security awareness** — you are connecting a messaging channel (WhatsApp, Telegram, etc.) to an AI with access to your local system. You need to understand what that means and configure it accordingly
- **Dependency awareness** — the stack includes OpenClaw, Node.js, Python, Pi-hole (optional), and Anthropic's API. You are responsible for understanding what each component does and does not do

### You run this at your own risk

ClawTutor is provided **as-is, without any warranty**. The authors accept no liability for:
- Data loss, system compromise, or unexpected AI behaviour
- Costs incurred through Anthropic API usage
- Any consequences arising from misconfiguration or security gaps in your setup

### Regular maintenance is required

A self-hosted system is only as secure as its last update. You are responsible for:

| Component | What to maintain |
|-----------|-----------------|
| **Raspberry Pi OS** | `sudo apt update && sudo apt upgrade` — regularly, especially security patches |
| **OpenClaw** | `npm update -g openclaw` — follow the [changelog](https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md) |
| **Node.js** | Keep on a supported LTS version (22+) |
| **Pi-hole** (if used) | Update via the Pi-hole admin panel |
| **Anthropic API** | Monitor for model deprecations and update model IDs in your config |

**Why Raspberry Pi?** Running ClawTutor on a dedicated [Raspberry Pi 5](https://www.raspberrypi.com/products/raspberry-pi-5/) (4 GB+) keeps it isolated from your main computers. If something goes wrong — a dependency vulnerability, a misconfiguration, an unexpected AI action — the blast radius is contained to a €80 device that can be wiped and re-flashed in minutes. It is also always on, low power, and easy to physically secure at home.

If you are not comfortable managing a Linux server and its security, consider waiting for a managed hosted version, or ask someone with the relevant skills to help with the initial setup and ongoing maintenance.

---

## 🤝 Built With

| Project | Role |
|---------|------|
| [OpenClaw](https://openclaw.ai) | AI agent gateway — the engine that runs everything |
| [Anthropic Claude](https://anthropic.com) | Claude Opus 4.5 (orchestrator) + Sonnet 4 (tutors) |
| [Raspberry Pi 5](https://www.raspberrypi.com/products/raspberry-pi-5/) 4 GB+ | Recommended self-hosted hardware platform |
| [Pi-hole](https://pi-hole.net) | DNS-based device control layer (optional) |
| [Home Assistant](https://home-assistant.io) | Power control via smart plugs (optional) |
| [SQLite](https://sqlite.org) | Local screen time credit database |
| WhatsApp / Telegram / Signal / Discord | Messaging channels — via OpenClaw gateway |

→ Full details on the [Built on](https://clawtutor.ai/ecosystem.html) page.

---

## 📄 License

Free for personal, family, and non-commercial use — attribution required.
Commercial use requires written permission. See [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- My kids, for being the ultimate QA testers (and for trying *very hard* to jailbreak Matteo)
- The OpenClaw team for making AI agents accessible
- Every parent who understands the screen time struggle

---

*Made with 🦞 by a parent who turned "Can I watch TV?" into "Can I do another quiz?"*
