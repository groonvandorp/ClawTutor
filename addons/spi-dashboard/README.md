# 🖥️ Dashboard Add-on (Mission Control)

**Optional physical display showing ClawTutor status on a small SPI screen.**

> ⚠️ **This is an optional add-on.** Make sure you have the [core system](../README.md) running first.

---

## Overview

A 3.5" display attached to your Pi showing:
- Credit balances for each kid
- Current streaks
- Active TV sessions (if using TV add-on)
- Upcoming exams
- System health

Perfect for a quick glance without opening your phone.

```
┌────────────────────────────────────┐
│  🎓 CLAWTUTOR MISSION CONTROL      │
├────────────────────────────────────┤
│ 👧 Kid 1       │ 👦 Kid 2          │
│ 45 min ⏱️      │ 30 min ⏱️         │
│ Streak: 3 🔥   │ Streak: 1         │
├────────────────────────────────────┤
│ 📺 TV: Beamer (Kid 2) 25m left     │
├────────────────────────────────────┤
│ 📅 Math test: 5 days               │
│ 💾 System: OK                      │
└────────────────────────────────────┘
```

---

## Hardware

| Component | Example | ~Cost |
|-----------|---------|-------|
| 3.5" SPI Display | Waveshare 3.5" (ILI9486) | €20-30 |
| Ribbon cable | Usually included | - |

The display connects to the Pi's GPIO header.

---

## Setup

### 1. Connect the Display

Attach the SPI display to your Pi's 40-pin GPIO header. Most 3.5" displays use:
- SPI0 (pins 19, 21, 23, 24, 26)
- Power (pins 1, 2, 17)
- Ground (pins 6, 9, 14, 20, 25)

### 2. Enable SPI and Framebuffer

Edit `/boot/config.txt`:

```ini
# Enable SPI
dtparam=spi=on

# Add overlay for your specific display
# Example for ILI9486 (check your display's documentation):
dtoverlay=piscreen,speed=16000000,rotate=270
```

Reboot and verify:
```bash
ls /dev/fb*
# Should show /dev/fb0 (HDMI) and /dev/fb1 (SPI)
```

### 3. Install Dependencies

```bash
sudo apt install python3-pil fonts-dejavu
pip3 install pillow
```

### 4. Configure the Script

Edit `addons/spi-dashboard/mission_control.py`:

```python
# Your tutor workspaces
TUTOR_KID1 = Path("~/.openclaw/workspace-tutor-kid1")
TUTOR_KID2 = Path("~/.openclaw/workspace-tutor-kid2")

# Display names
# In render_child_card calls, change "Kid 1"/"Kid 2" to actual names
```

### 5. Test It

```bash
cd ~/.openclaw/workspace
python3 addons/spi-dashboard/mission_control.py
```

You should see the dashboard appear on the SPI screen.

### 6. Run as Service

Copy the included service file:

```bash
sudo cp addons/spi-dashboard/mission-control.service /etc/systemd/system/
```

Enable and start:
```bash
sudo systemctl enable mission-control
sudo systemctl start mission-control
```

---

## Customization

### Change Colors

Edit the color constants at the top of `addons/spi-dashboard/mission_control.py`:

```python
BG = (15, 15, 25)        # Background
GREEN = (0, 200, 100)    # Good status
RED = (220, 50, 50)      # Warning
YELLOW = (255, 200, 0)   # Caution
```

### Change Refresh Rate

```python
REFRESH_INTERVAL = 30  # seconds
```

### Add More Kids

Add more workspace paths and `render_child_card()` calls.

---

## Troubleshooting

### Display shows nothing
- Check SPI is enabled: `lsmod | grep spi`
- Verify framebuffer exists: `ls /dev/fb1`
- Try writing test pattern: `cat /dev/urandom > /dev/fb1`

### Wrong orientation
- Adjust `rotate=` parameter in config.txt overlay
- Or set `ROTATION` in the Python script

### Fonts look wrong
- Install DejaVu fonts: `sudo apt install fonts-dejavu`
- Check font paths in the script

---

*This add-on is purely optional — ClawTutor works fine without a physical display!*
