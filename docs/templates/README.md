# 📋 Templates

Copy these files into a new child's workspace to get started.

## Required Files

| File | Purpose |
|------|---------|
| `SOUL.md` | Tutor router, security rules, screen time system |
| `AGENTS.md` | Agent startup instructions |
| `MODE.md` | Active tutor state (starts as Matteo) |
| `USER.md` | Child's info (fill in) |
| `SCREENTIME.md` | Screen time reward tracking |

## Also Needed (from classes/)

Copy the curriculum and progress files for the child's grade:

| File | Source |
|------|--------|
| `CURRICULUM.md` | From `classes/math-X/` |
| `CURRICULUM-ENGLISH.md` | From `classes/english-X/` |
| `PROGRESS.md` | From `classes/math-X/` |
| `PROGRESS-ENGLISH.md` | From `classes/english-X/` |

## Also Needed (from tutors/)

| File | Source |
|------|--------|
| `MATTEO.md` | From `tutors/matteo/` |
| `NELLY.md` | From `tutors/nelly/` |

## Quick Setup

```bash
WORKSPACE=~/.openclaw/workspace-tutor-CHILDNAME
mkdir -p $WORKSPACE/subjects/english/{vocab,grammar,exercises} $WORKSPACE/memory

# Copy templates
cp templates/{SOUL,AGENTS,MODE,USER,SCREENTIME}.md $WORKSPACE/

# Copy tutor personalities
cp tutors/matteo/MATTEO.md $WORKSPACE/
cp tutors/nelly/NELLY.md $WORKSPACE/

# Copy class files (adjust grade!)
cp classes/math-7/CURRICULUM.md $WORKSPACE/
cp classes/math-7/PROGRESS.md $WORKSPACE/
cp classes/english-7/CURRICULUM.md $WORKSPACE/CURRICULUM-ENGLISH.md
cp classes/english-7/PROGRESS.md $WORKSPACE/PROGRESS-ENGLISH.md

# Edit USER.md with child's info
nano $WORKSPACE/USER.md
```
