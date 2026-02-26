# 🖥️ Web Dashboard

**Browser-based dashboard to monitor ClawTutor status from any device.**

---

## Overview

A responsive web dashboard showing:
- 💰 Screen time balances for each kid
- 📊 Recent activity (earned/spent time)
- 📺 Device status (TVs, Switch, etc.)
- ⏱️ Active sessions

Access from any device on your network.

---

## Access

Once the tutor-api is running:

```
http://<PI_IP>:3847/dashboard
```

Example: `http://192.168.2.47:3847/dashboard`

---

## Features

### Real-time Updates
- Auto-refreshes every 30 seconds
- Manual refresh by reloading the page

### Responsive Design
- Works on desktop, tablet, and mobile
- Dark theme for comfortable viewing

### Status Indicators
- 🟢 Green: System healthy
- 🟡 Yellow: Partial issues
- 🔴 Red: System offline

---

## Screenshots

```
┌────────────────────────────────────────────────────────┐
│  🎓 ClawTutor Dashboard                    16:15      │
│                                         24. Feb 2026   │
├────────────────────────────────────────────────────────┤
│  ● API  ● Gateway  Letzte Aktualisierung: 16:15:30    │
├────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐             │
│  │ 👧 Lena       │  │ 👦 Max       │             │
│  │    45 Min       │  │    30 Min       │             │
│  │ ─────────────── │  │ ─────────────── │             │
│  │ +10 Quiz Mathe  │  │ +10 Quiz Mathe  │             │
│  │ -20 TV Beamer   │  │ +5 Streak Bonus │             │
│  └─────────────────┘  └─────────────────┘             │
├────────────────────────────────────────────────────────┤
│  📺 Geräte                                             │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │
│  │📽️ Beamer │ │🖥️ LCD    │ │📺 Wohnz. │ │🎮 Switch │ │
│  │ Gesperrt │ │ Gesperrt │ │ Gesperrt │ │ Gesperrt │ │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ │
└────────────────────────────────────────────────────────┘
```

---

## Technical Details

- **Part of:** tutor-api (no separate service needed)
- **Port:** 3847 (same as REST API)
- **Technology:** Static HTML + Vanilla JavaScript
- **Data source:** Existing API endpoints

### API Endpoints Used

| Endpoint | Description |
|----------|-------------|
| `/api/profiles` | Get kids + balances |
| `/api/history/:kind` | Recent transactions |
| `/api/tv/status` | Device status |

---

## Customization

Edit `tutor-api/public/dashboard.html` to:
- Change colors (CSS variables at top)
- Add more kids
- Modify refresh interval
- Add additional data

---

*The dashboard is read-only. Use WhatsApp or the iOS app to control devices.*
