# ClawTutor: Building an AI Tutoring System for My Kids with OpenClaw

*How I turned a Raspberry Pi into a personalized, WhatsApp-based learning companion for my 10 and 13-year-old*

---

## The Problem

My kids, like most, weren't thrilled about homework. The usual dynamic: they'd ask for help, I'd explain something, they'd nod, and 20 minutes later we'd be back at square one. Traditional tutoring apps felt sterile. YouTube videos were hit-or-miss. And let's be honest — screen time was the real currency in our house.

So I thought: what if I could build something that:
- **Meets them where they are** (WhatsApp, not another app)
- **Adapts to how they learn** (not one-size-fits-all explanations)
- **Never gives away answers** (but guides them there)
- **Rewards effort with what they actually want** (screen time)

The result is **ClawTutor** — an AI tutoring system running on a Raspberry Pi 5, powered by [OpenClaw](https://github.com/openclaw/openclaw) and Claude.

---

## The Setup

### Hardware
- Raspberry Pi 5 (4GB)
- That's it. Seriously.

### Software Stack
- **OpenClaw** — The AI gateway that handles WhatsApp integration, agent management, and session orchestration
- **Claude Sonnet 4** — The LLM brain (Opus for my personal assistant, Sonnet for the tutors to keep costs reasonable)
- **Pi-hole** — DNS-based screen time control (more on this later)
- **SQLite** — Progress tracking and screen time ledger

### Architecture

```
WhatsApp ←→ OpenClaw Gateway ←→ Claude API
                ↓
         Agent: "tutor-arthur"
                ↓
         Workspace Files:
         - SOUL.md (personality)
         - CURRICULUM.md (what to teach)
         - PROGRESS.md (what they've learned)
         - LEARNING_PROFILE.md (how they learn)
```

Each kid gets their own agent with its own workspace. The agent reads its "soul" file to know how to behave, checks the curriculum to know what to teach, and tracks everything in progress files.

---

## The Tutors

My kids don't talk to "ClawTutor." They talk to **Matteo** (math), **Nelly** (English), and **Melody** (music theory). Each has a distinct personality:

**Matteo 🧮** is patient and encouraging. He never gets frustrated, even when my son asks the same question five different ways. He uses everyday examples: "If you have 3 Pokémon packs at €5 each..."

**Nelly 🇬🇧** is the cool English tutor who mixes German and English naturally. She makes vocabulary feel less like memorization and more like unlocking a secret code.

**Melody 🎹** teaches music theory with a focus on our Korg Monologue synthesizer. She explains chords as arpeggios (since it's a mono synth) and uses Bach's Prelude in C Major as teaching material.

Switching is simple:
```
Arthur: /mathe
Matteo: Hey! Matteo hier 🧮 Was rechnen wir?
```

---

## The Secret Sauce: Never Give the Answer

The hardest part wasn't the tech — it was the pedagogy. Every LLM wants to be helpful, which usually means giving you the answer. But that's terrible for learning.

The tutors are explicitly instructed:

> **NEVER give a complete solution without explanation — even if they beg.**
> Instead: hints, partial steps, questions that prompt thinking.
> If they say "just tell me the answer": "That's not how you learn 😉 Let's work through this together!"

This is enforced in the `SOUL.md` file and surprisingly, Claude respects it well. My kids have tried everything — begging, pretending to be me, claiming it's an emergency. The tutor just... stays in character.

---

## Learning Types: Teaching How *They* Learn

Not every kid learns the same way. My daughter absorbs information by reading and making lists. My son needs to see it in action — "imagine you're at the store buying..."

We implemented the VARK model (Visual, Auditory, Read/Write, Kinesthetic) with a simple onboarding flow:

```
Matteo: Quick question before we start — when you learn something new,
        what helps most?
        
        A) Reading about it 📖
        B) Trying it out right away 🎮
        C) Someone explaining it to me 🗣️
        D) Seeing a picture or diagram 📊
```

Four questions later, the tutor knows how to adapt. A kinesthetic learner gets real-world scenarios first, then the formula. A read/write learner gets the rule first, then examples.

The profile is stored in `LEARNING_PROFILE.md` and the tutor reads it every session.

---

## The Motivation Engine: Screen Time as Currency

Here's where it gets interesting. My kids *want* to do their quizzes because correct answers = screen time.

The economy:
- **10 minutes** per correct answer
- **+10 bonus** for a perfect quiz (3/3)
- **Streak bonuses** — 5 days in a row = +30 minutes weekend bonus
- **Break the streak** = back to zero

This is tracked in a SQLite database with a native OpenClaw plugin. The tutors can query balances and add time:

```javascript
screentime_add(kind: "arthur", minutes: 40, reason: "Quiz 3/3 + Bonus")
```

But here's the kicker: the tutors can't *spend* the time. Only I (or my wife, via a separate "parents" agent) can unlock the TV:

```
Parent: tv wohnzimmer 30 min arthur
System: ✅ Wohnzimmer unlocked for 30 minutes. Auto-off at 18:45.
```

Under the hood, this uses Pi-hole to block our Apple TVs at the DNS level. When time's up, the DNS block goes back on. No app needed on the TV, no parental control software to configure. Just DNS.

---

## Exam Prep Mode

When a test is coming up, everything shifts focus. We track exams in a `CALENDAR.md` file:

| Date | Subject | Topic | Status |
|------|---------|-------|--------|
| 20.03.2026 | Math | Fractions | 🟡 14 days |

The tutor automatically adjusts:
- **14 days out**: Cover all subtopics
- **7 days out**: Focus on weak areas (from PROGRESS.md)
- **3 days out**: Mixed practice like the real test
- **1 day before**: Mini mock exam
- **Test day**: Just encouragement, no quiz

This happened automatically when we added the calendar entry. No extra configuration.

---

## What I Learned

### 1. Personality matters more than capability
Claude can solve any math problem my kids throw at it. But that's not the point. The *way* Matteo talks — patient, encouraging, using their language — that's what makes them actually engage.

### 2. Constraints make better teachers
Telling the LLM what NOT to do (give answers directly) was more important than what to do. The `SOUL.md` file is mostly constraints.

### 3. Meet them where they are
WhatsApp was non-negotiable. My kids live there. Adding another app would have been DOA.

### 4. Incentives need to be real
Theoretical points don't work. Screen time — the thing they actually want — does.

### 5. It's not about replacing teachers
ClawTutor handles the daily practice grind. It frees up my time for the moments where they need a human — the frustration, the "I'll never get this," the celebration when something clicks.

---

## What's Next

- **MIDI integration for Melody** — The Korg can send note data; imagine real-time feedback on piano practice
- **Voice output via Bluetooth speaker** — Announcements like "Arthur, time for your quiz!"
- **iOS app** — Currently in testing, native chat interface instead of WhatsApp
- **Adaptive difficulty** — Automatically adjust based on performance trends

---

## Try It Yourself

ClawTutor is built on [OpenClaw](https://github.com/openclaw/openclaw), which is open source. The tutoring logic is just markdown files and a bit of configuration.

If you want to build something similar:
1. Set up OpenClaw on a Pi (or any Linux box)
2. Connect WhatsApp via the built-in bridge
3. Create an agent with a workspace
4. Write your `SOUL.md` with the tutor personality
5. Add curriculum and progress tracking

The hardest part is writing good prompts. But once you nail the personality, it kind of... works.

---

*Questions? Find me on the [OpenClaw Discord](https://discord.com/invite/clawd) or open an issue on GitHub.*

---

**Tags:** #AI #Education #OpenClaw #RaspberryPi #Parenting #LLM #Claude
