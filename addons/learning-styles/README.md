# Add-on: Learning Styles (VARK)

Optional extension for ClawTutor that determines a child's learning type and adapts the tutor's teaching style accordingly.

## What is this?

Based on the VARK model:
- **V**isual — learns through images, diagrams, spatial representation
- **A**uditory — learns through listening, explaining, discussion
- **R**ead/Write — learns through reading, lists, notes
- **K**inesthetic — learns through touching, trying, movement

## Installation

1. Copy `PROFILE_TEMPLATE.md` to the child's workspace as `LEARNING_PROFILE.md`
2. Add the content of `tutor-patch.md` to the tutor's SOUL.md
3. Optional: Use `ONBOARDING.md` for the learning type assessment on first contact

## Files

| File | Purpose |
|------|---------|
| `README.md` | This guide |
| `ONBOARDING.md` | 4-question assessment to determine learning type |
| `PROFILE_TEMPLATE.md` | Template for the learning profile |
| `tutor-patch.md` | Addition to the tutor's SOUL.md |

## Usage

### With Onboarding (recommended)
On first contact, the tutor runs a short assessment and creates the profile automatically.

### Without Onboarding
Parents/teachers can also fill in the profile manually if they already know the learning type.

### Disabling
Simply delete `LEARNING_PROFILE.md` or set `type: unknown` — the tutor will then behave neutrally.

## Note

The VARK model is a simplified tool. Children aren't fixed types — most learn multimodally. The tutor uses the learning type as a starting point, not a label.
