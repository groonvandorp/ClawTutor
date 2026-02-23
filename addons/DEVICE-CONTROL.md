# 🔒 Device Control Add-on

**Optional module to automatically enforce screen time limits via DNS blocking.**

> ⚠️ **This is an optional add-on.** Make sure you have the [core system](../README.md) running first.

---

## Overview

Instead of manually checking balances and trusting kids to self-regulate, this add-on:
- **Blocks any network device** by default via Pi-hole DNS
- **Unblocks on request** when kids have sufficient credits
- **Auto-locks** after the approved time expires
- **Integrates with WhatsApp** — kids request device time via chat

### Supported Devices

| Type | Examples |
|------|----------|
| 📺 **Smart TVs** | Apple TV, Fire TV, Chromecast, Android TV, Roku |
| 🎮 **Gaming** | PlayStation 4/5, Xbox, Nintendo Switch |
| 📱 **Mobile** | iPhones, iPads, Android phones/tablets |
| 💻 **Computers** | Laptops, PCs, Chromebooks |

**Any device that uses your network can be controlled.**

---

## How It Works

```
Kid: "30 min PlayStation bitte"
     ↓
Tutor: checks balance (45 min available)
     ↓
System: unblocks PlayStation, starts 30-min timer
     ↓
30 min later: auto-blocks PlayStation
     ↓
Balance: 15 min remaining
```

---

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│                     Raspberry Pi                          │
│                                                           │
│  ┌─────────────┐    ┌─────────────┐    ┌──────────────┐ │
│  │  ClawTutor  │───▶│  Pi-hole    │───▶│  DNS Block   │ │
│  │  (credits)  │    │  API        │    │  per Device  │ │
│  └─────────────┘    └─────────────┘    └──────────────┘ │
│                                                           │
│  ┌─────────────┐                                         │
│  │  Cron Job   │ ← checks every 2 min for expired       │
│  │  (auto-off) │   sessions and re-blocks devices       │
│  └─────────────┘                                         │
└──────────────────────────────────────────────────────────┘
           │
           │ DNS queries
           ▼
    ┌─────────────────────────────────────────────────┐
    │  📺 TV    🎮 PlayStation    📱 Phone    💻 PC   │
    │         (blocked = no internet/streaming)       │
    └─────────────────────────────────────────────────┘
```

---

## Requirements

- **Pi-hole v6+** running on the same Pi (or accessible via API)
- **Devices** configured to use Pi-hole as DNS server
- ClawTutor core system with screen time credits working

---

## Setup

### 1. Install Pi-hole

```bash
curl -sSL https://install.pi-hole.net | bash
```

During setup:
- Set a web admin password (you'll need it for the API)
- Note the admin URL (usually `http://pi.hole/admin` or `http://YOUR_PI_IP/admin`)

### 2. Configure Devices to Use Pi-hole DNS

#### Option A: Per-Device (Recommended for Control)

Configure DNS manually on each device you want to control:

| Device | How to Configure |
|--------|------------------|
| **Apple TV** | Settings → Network → Wi-Fi → Configure DNS → Manual |
| **PlayStation** | Settings → Network → Set Up Connection → Custom → DNS |
| **Xbox** | Settings → Network → Advanced → DNS |
| **Nintendo Switch** | System Settings → Internet → DNS Settings → Manual |
| **iPhone/iPad** | Settings → Wi-Fi → (i) → Configure DNS → Manual |
| **Android** | Settings → Wi-Fi → Long-press network → Modify → Advanced → DNS |

Enter your Pi's IP address (e.g., `192.168.1.100`)

#### Option B: Router-Level (Blocks Everything)

Set your router's DHCP to distribute Pi-hole as DNS server. This blocks all devices by default.

### 3. Create Device Groups in Pi-hole

1. Open Pi-hole admin → Group Management → Groups
2. Create groups for device types:
   - `Gaming_Blocked`
   - `Mobile_Blocked`
   - `TV_Blocked`
   - (or just one `Kids_Blocked` group)

3. Go to Domains → Add blocking rule:
   - Domain: `.*` (regex for all domains)
   - Type: Regex blacklist
   - Group: Your blocked group

### 4. Register Devices as Clients

1. Go to Group Management → Clients
2. Add each device by MAC address:
   - Comment: `Kid1 PlayStation`, `Kid2 iPhone`, etc.
   - Group: Default (allowed) initially

**Finding MAC addresses:**
- Check your router's DHCP leases
- Or: `sudo arp-scan --localnet`

### 5. Configure the Device Registry

Edit `scripts/device-access.sh`:

```bash
PIHOLE_API="http://localhost/api"
PIHOLE_PASSWORD="${PIHOLE_PASSWORD:-your-password-here}"

# Device registry — add all controlled devices
declare -A DEVICES=(
    # TVs
    ["beamer"]="AA:BB:CC:DD:EE:01"
    ["wohnzimmer_tv"]="AA:BB:CC:DD:EE:02"
    
    # Gaming
    ["playstation"]="AA:BB:CC:DD:EE:03"
    ["switch"]="AA:BB:CC:DD:EE:04"
    ["xbox"]="AA:BB:CC:DD:EE:05"
    
    # Mobile
    ["kid1_handy"]="AA:BB:CC:DD:EE:06"
    ["kid2_tablet"]="AA:BB:CC:DD:EE:07"
    
    # Computers
    ["kid1_laptop"]="AA:BB:CC:DD:EE:08"
)

# Device types (for group control)
declare -A DEVICE_TYPES=(
    ["beamer"]="tv"
    ["wohnzimmer_tv"]="tv"
    ["playstation"]="gaming"
    ["switch"]="gaming"
    ["xbox"]="gaming"
    ["kid1_handy"]="mobile"
    ["kid2_tablet"]="mobile"
    ["kid1_laptop"]="computer"
)

# Device owners (for per-kid control)
declare -A DEVICE_OWNERS=(
    ["playstation"]="kid1"
    ["switch"]="kid1"
    ["kid1_handy"]="kid1"
    ["kid2_tablet"]="kid2"
)
```

**Security tip:** Set the password via environment variable:
```bash
export PIHOLE_PASSWORD="your-actual-password"
```

### 6. Set Up Auto-Off Cron Job

```bash
crontab -e
```

Add:
```
*/2 * * * * /home/YOUR_USER/.openclaw/workspace/scripts/device-auto-off.sh
```

### 7. Test It

```bash
# Block all gaming devices
./scripts/device-access.sh block gaming

# Allow specific device
./scripts/device-access.sh allow playstation

# Check status
./scripts/device-access.sh status all

# Start timed session (deducts credits)
./scripts/device-session.sh start kid1 playstation 30

# Check active sessions
sqlite3 data/screentime.db "SELECT * FROM device_sessions WHERE status='active';"
```

---

## Usage

### Manual Control (Parents)

```bash
# By device name
./scripts/device-access.sh block playstation
./scripts/device-access.sh allow switch

# By device type
./scripts/device-access.sh block gaming    # all gaming devices
./scripts/device-access.sh allow tv        # all TVs

# By owner
./scripts/device-access.sh block kid1    # all of Kid 1's devices
./scripts/device-access.sh allow kid2    # all of Kid 2's devices

# Everything
./scripts/device-access.sh block all
./scripts/device-access.sh status all
```

Or via WhatsApp to your main agent:
- "PlayStation aus" → blocks PlayStation
- "Alle Geräte aus" → blocks everything
- "Kid1 Geräte an" → allows all of Kid 1's devices
- "Status" → shows current state

### Kid Requests (via Tutor)

Kids text their tutor:
- "30 min PlayStation bitte"
- "Kann ich eine Stunde Switch spielen?"
- "Ich möchte fernsehen"

The tutor:
1. Checks their credit balance
2. If sufficient: approves, deducts credits, starts session
3. If insufficient: tells them how much they need to earn

### Session Flow

1. **Request:** Kid asks for device time
2. **Check:** System verifies credits ≥ requested time
3. **Deduct:** Credits subtracted from balance
4. **Unblock:** Pi-hole allows the device
5. **Timer:** Session recorded with end time
6. **Auto-off:** Cron job re-blocks when time expires

---

## Database Schema

The add-on extends `screentime.db`:

```sql
CREATE TABLE device_sessions (
    id INTEGER PRIMARY KEY,
    kind TEXT NOT NULL,           -- "kid1", "kid2"
    device TEXT NOT NULL,         -- "playstation", "switch", etc.
    device_type TEXT,             -- "gaming", "tv", "mobile"
    minutes INTEGER NOT NULL,     -- duration
    started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    ends_at DATETIME NOT NULL,
    ended_at DATETIME,            -- actual end (or NULL if active)
    status TEXT DEFAULT 'active'  -- "active" or "ended"
);
```

---

## Advanced: Device Categories

You can set rules per device type:

```bash
# Example: Gaming allowed only after 15:00
# Add to your main agent's SOUL.md or cron:

# Morning block (school hours)
./scripts/device-access.sh block gaming   # 08:00
./scripts/device-access.sh block mobile   # 08:00

# Afternoon allow (if credits available)
# (or keep blocked and require credit-based unlock)
```

---

## Troubleshooting

### Device still works when blocked
- Check DNS settings on the device (must point to Pi-hole)
- Verify the MAC address is correct in your registry
- Some devices cache DNS — restart them after blocking
- Check Pi-hole logs for queries from that device

### Gaming console works but can't play online
That's probably correct! DNS blocking stops online services. Offline games may still work.

### Mobile device uses cellular data
DNS blocking only works on Wi-Fi. Mobile data bypasses your network entirely. Consider:
- Using built-in parental controls (iOS Screen Time, Android Family Link)
- Disabling cellular data on kids' devices

### Session doesn't auto-end
- Verify cron job is running: `crontab -l`
- Check logs: `tail -f ~/.openclaw/workspace/logs/device-auto-off.log`
- Ensure script has execute permission

### Pi-hole API errors
- Test authentication: `curl -X POST http://localhost/api/auth -d '{"password":"xxx"}'`
- Check Pi-hole version (needs v6+)
- Verify the password is correct

---

## Platform-Specific Notes

### Nintendo Switch
- Blocking DNS stops eShop and online play
- Offline games and local multiplayer still work
- For full control, also enable Nintendo Parental Controls app

### PlayStation
- DNS blocking stops PSN, streaming apps, online games
- Offline games still work
- Some games require online check even for single-player

### Mobile Devices
- Works on Wi-Fi only — cellular bypasses DNS
- Consider combining with iOS Screen Time / Android Family Link
- Blocking DNS breaks most apps (including messaging)

### Smart TVs
- Streaming apps (Netflix, YouTube) stop working
- Local media (USB, DLNA) still works
- Some TVs try fallback DNS — check your router settings

---

## Security Notes

- Pi-hole password should not be committed to git
- Use environment variables or a separate credentials file
- The main agent needs `exec` tool access to run the scripts
- Tutor agents should NOT have direct device control — they request via the main agent
- Kids who know networking might change their DNS settings — consider router-level enforcement

---

*This add-on is optional. ClawTutor works great with manual screen time management too!*
