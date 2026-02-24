#!/usr/bin/env python3
"""
Mission Control Dashboard for OpenClaw / ClawTutor
Displays on SPI TFT (480x320, /dev/fb1)
"""

import os
import sys
import json
import time
import subprocess
import signal
import re
import sqlite3
from datetime import datetime, date
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# Config
FB_DEVICE = "/dev/fb1"
WIDTH = 480
HEIGHT = 320
REFRESH_INTERVAL = 30  # seconds
WORKSPACE = Path(os.path.expanduser("~/.openclaw"))
# Configure your tutor workspaces here:
TUTOR_KID1 = Path(os.path.expanduser("~/.openclaw/workspace-tutor-kid1"))
TUTOR_KID2 = Path(os.path.expanduser("~/.openclaw/workspace-tutor-kid2"))
# INFOSEC_WS = Path(os.path.expanduser("~/.openclaw/workspace-infosec"))

# Colors (RGB)
BG = (15, 15, 25)
HEADER_BG = (30, 30, 50)
CARD_BG = (25, 30, 45)
GREEN = (0, 200, 100)
RED = (220, 50, 50)
YELLOW = (255, 200, 0)
BLUE = (60, 120, 255)
ORANGE = (255, 140, 40)
PURPLE = (160, 100, 255)
TEAL = (0, 180, 170)
WHITE = (255, 255, 255)
GRAY = (150, 150, 170)
DIM = (80, 80, 100)

# Fonts
try:
    FONT_BIG = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
    FONT_MED = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
    FONT_SMALL = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 13)
    FONT_TINY = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
    FONT_ICON = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
except:
    FONT_BIG = ImageFont.load_default()
    FONT_MED = ImageFont.load_default()
    FONT_SMALL = ImageFont.load_default()
    FONT_TINY = ImageFont.load_default()
    FONT_ICON = ImageFont.load_default()


def get_cpu_temp():
    try:
        temp = open("/sys/class/thermal/thermal_zone0/temp").read().strip()
        return f"{int(temp) / 1000:.1f}°C"
    except:
        return "?"


def get_uptime():
    try:
        up = float(open("/proc/uptime").read().split()[0])
        hours = int(up // 3600)
        mins = int((up % 3600) // 60)
        if hours > 24:
            days = hours // 24
            hours = hours % 24
            return f"{days}d {hours}h"
        return f"{hours}h {mins}m"
    except:
        return "?"


def get_memory_usage():
    try:
        with open("/proc/meminfo") as f:
            lines = f.readlines()
        total = int(lines[0].split()[1])
        available = int(lines[2].split()[1])
        used_pct = int((1 - available / total) * 100)
        return f"{used_pct}%"
    except:
        return "?"


def get_whatsapp_status():
    """Check both WhatsApp accounts"""
    try:
        result = subprocess.run(
            ["openclaw", "status"],
            capture_output=True, text=True, timeout=15
        )
        output = result.stdout + result.stderr
        accounts_match = re.search(r"accounts (\d+)", output)
        num_accounts = int(accounts_match.group(1)) if accounts_match else 0
        
        if "linked" in output.lower() or "connected" in output.lower():
            return True, f"{num_accounts} accounts"
        return False, "Disconnected"
    except:
        return False, "Error"


def get_gateway_status():
    try:
        result = subprocess.run(
            ["openclaw", "gateway", "status"],
            capture_output=True, text=True, timeout=10
        )
        if "running" in result.stdout.lower():
            return True
        return False
    except:
        return False


def read_active_tutor(workspace_path):
    """Read MODE.md to see which tutor is active"""
    mode_file = Path(workspace_path) / "MODE.md"
    try:
        content = mode_file.read_text()
        if "english" in content.lower():
            return "Nelly", "EN"
        return "Matteo", "MA"
    except:
        return "Matteo", "MA"


def read_progress(workspace_path, english=False):
    """Read PROGRESS.md and extract stats"""
    filename = "PROGRESS-ENGLISH.md" if english else "PROGRESS.md"
    progress_file = Path(workspace_path) / filename
    try:
        content = progress_file.read_text()
        total_right = 0
        total_wrong = 0
        topics_tested = 0
        weak_topics = []
        
        for line in content.split("\n"):
            if "|" in line and "nicht getestet" not in line and "---" not in line:
                parts = [p.strip() for p in line.split("|")]
                if len(parts) >= 6:
                    try:
                        right = int(parts[3])
                        wrong = int(parts[4])
                        if right + wrong > 0:
                            topics_tested += 1
                            total_right += right
                            total_wrong += wrong
                            if "🟡" in parts[2]:
                                weak_topics.append(parts[1])
                    except (ValueError, IndexError):
                        pass
        
        total = total_right + total_wrong
        quote = f"{int(total_right / total * 100)}%" if total > 0 else "--"
        return {
            "tested": topics_tested,
            "right": total_right,
            "wrong": total_wrong,
            "quote": quote,
            "weak": weak_topics[:2]
        }
    except:
        return {"tested": 0, "right": 0, "wrong": 0, "quote": "--", "weak": []}


def read_screentime(workspace_path):
    """Read SCREENTIME.md and extract weekly total + streak (legacy fallback)"""
    st_file = Path(workspace_path) / "SCREENTIME.md"
    try:
        content = st_file.read_text()
        total_match = re.search(r"Wochenguthaben:\s*(\d+)\s*Min", content)
        streak_match = re.search(r"Streak:\s*(\d+)\s*Tage", content)
        total = int(total_match.group(1)) if total_match else 0
        streak = int(streak_match.group(1)) if streak_match else 0
        return total, streak
    except:
        return 0, 0


def read_screentime_db(kind):
    """Read screen time budget from SQLite DB"""
    db_path = Path(os.path.expanduser("~/.openclaw/workspace/data/screentime.db"))
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Get budget
        cursor.execute("SELECT balance_minutes FROM budget WHERE kind = ?", (kind,))
        row = cursor.fetchone()
        balance = row[0] if row else 0
        
        # Check for active TV session
        cursor.execute(
            "SELECT tv, minutes, ends_at FROM tv_sessions WHERE kind = ? AND status = 'active'",
            (kind,)
        )
        active = cursor.fetchone()
        
        conn.close()
        
        return {
            "balance": balance,
            "active_tv": active[0] if active else None,
            "active_minutes": active[1] if active else 0,
            "active_ends": active[2] if active else None
        }
    except Exception as e:
        return {"balance": 0, "active_tv": None, "active_minutes": 0, "active_ends": None}


def read_exams(workspace_path):
    """Read CALENDAR.md and return upcoming exams"""
    cal_file = Path(workspace_path) / "CALENDAR.md"
    exams = []
    try:
        content = cal_file.read_text()
        today = date.today()
        for line in content.split("\n"):
            if "|" in line and "Datum" not in line and "---" not in line and "noch keine" not in line:
                parts = [p.strip() for p in line.split("|")]
                if len(parts) >= 5 and parts[1]:
                    try:
                        exam_date = datetime.strptime(parts[1], "%d.%m.%Y").date()
                        days_left = (exam_date - today).days
                        if days_left >= 0:
                            exams.append({
                                "date": parts[1],
                                "subject": parts[2],
                                "topic": parts[3],
                                "days": days_left
                            })
                    except (ValueError, IndexError):
                        pass
    except:
        pass
    return exams


def read_current_topic(workspace_path, english=False):
    """Read CURRICULUM and find current topic"""
    filename = "CURRICULUM-ENGLISH.md" if english else "CURRICULUM.md"
    curr_file = Path(workspace_path) / filename
    try:
        content = curr_file.read_text()
        for line in content.split("\n"):
            if "AKTUELL" in line or "🔥" in line:
                # Extract topic name
                clean = re.sub(r'[#*🔥←]', '', line).strip()
                clean = re.sub(r'\(S\.\s*\d+.*?\)', '', clean).strip()
                clean = re.sub(r'AKTUELL', '', clean).strip()
                clean = re.sub(r'^[\s\-\.]+', '', clean).strip()
                if clean:
                    return clean[:25]
        return "---"
    except:
        return "---"


def draw_rounded_rect(draw, xy, radius, fill):
    x1, y1, x2, y2 = xy
    draw.rectangle([x1 + radius, y1, x2 - radius, y2], fill=fill)
    draw.rectangle([x1, y1 + radius, x2, y2 - radius], fill=fill)
    draw.pieslice([x1, y1, x1 + 2*radius, y1 + 2*radius], 180, 270, fill=fill)
    draw.pieslice([x2 - 2*radius, y1, x2, y1 + 2*radius], 270, 360, fill=fill)
    draw.pieslice([x1, y2 - 2*radius, x1 + 2*radius, y2], 90, 180, fill=fill)
    draw.pieslice([x2 - 2*radius, y2 - 2*radius, x2, y2], 0, 90, fill=fill)


def draw_progress_bar(draw, x, y, w, h, pct, color):
    draw_rounded_rect(draw, (x, y, x + w, y + h), 4, (40, 40, 60))
    if pct > 0:
        fill_w = max(8, int(w * pct / 100))
        draw_rounded_rect(draw, (x, y, x + fill_w, y + h), 4, color)


def render_child_card(draw, x, y, w, h, name, emoji, grade, color, workspace):
    """Render a child's card with both subjects"""
    draw_rounded_rect(draw, (x, y, x + w, y + h), 6, CARD_BG)
    
    # Header
    draw.text((x + 8, y + 4), f"{emoji} {name}", font=FONT_MED, fill=color)
    draw.text((x + w - 70, y + 6), f"{grade}. Klasse", font=FONT_SMALL, fill=GRAY)
    
    # Active tutor
    tutor_name, tutor_code = read_active_tutor(workspace)
    tutor_color = ORANGE if tutor_code == "MA" else PURPLE
    draw.text((x + w - 70, y + 20), f"[{tutor_name}]", font=FONT_TINY, fill=tutor_color)
    
    # Math stats
    math_topic = read_current_topic(workspace, english=False)
    math_prog = read_progress(workspace, english=False)
    
    draw.text((x + 8, y + 26), "MA", font=FONT_ICON, fill=ORANGE)
    draw.text((x + 28, y + 27), math_topic, font=FONT_SMALL, fill=WHITE)
    
    math_total = math_prog["right"] + math_prog["wrong"]
    if math_total > 0:
        pct = int(math_prog["right"] / math_total * 100)
        draw_progress_bar(draw, x + 8, y + 44, w - 75, 8, pct, GREEN)
        draw.text((x + w - 60, y + 41), math_prog["quote"], font=FONT_SMALL, fill=GREEN)
    else:
        draw.text((x + 8, y + 41), "noch keine Daten", font=FONT_TINY, fill=DIM)
    
    # English stats
    eng_topic = read_current_topic(workspace, english=True)
    eng_prog = read_progress(workspace, english=True)
    
    draw.text((x + 8, y + 56), "EN", font=FONT_ICON, fill=PURPLE)
    draw.text((x + 28, y + 57), eng_topic, font=FONT_SMALL, fill=WHITE)
    
    eng_total = eng_prog["right"] + eng_prog["wrong"]
    if eng_total > 0:
        pct = int(eng_prog["right"] / eng_total * 100)
        draw_progress_bar(draw, x + 8, y + 74, w - 75, 8, pct, BLUE)
        draw.text((x + w - 60, y + 71), eng_prog["quote"], font=FONT_SMALL, fill=BLUE)
    else:
        draw.text((x + 8, y + 71), "noch keine Daten", font=FONT_TINY, fill=DIM)
    
    # Screen time from DB
    kind = name.lower()  # e.g., "kid1" or "kid2"
    st_data = read_screentime_db(kind)
    balance = st_data["balance"]
    
    # Color based on balance
    if balance >= 30:
        st_color = GREEN
    elif balance >= 10:
        st_color = YELLOW
    else:
        st_color = RED
    
    draw.text((x + 8, y + 88), f"TV: {balance} Min", font=FONT_SMALL, fill=st_color)
    
    # Show active TV session if any
    if st_data["active_tv"]:
        draw.text((x + 90, y + 89), f"[{st_data['active_tv']}]", font=FONT_TINY, fill=ORANGE)
    
    # Stats
    total_right = math_prog["right"] + eng_prog["right"]
    total_wrong = math_prog["wrong"] + eng_prog["wrong"]
    draw.text((x + 8, y + 102), f"Gesamt: {total_right}R {total_wrong}F", font=FONT_TINY, fill=DIM)


def render_dashboard():
    img = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(img)
    
    now = datetime.now()
    
    # === HEADER ===
    draw.rectangle([0, 0, WIDTH, 36], fill=HEADER_BG)
    draw.text((10, 8), "ClawTutor", font=FONT_BIG, fill=BLUE)
    draw.text((130, 12), "MISSION CONTROL", font=FONT_SMALL, fill=DIM)
    time_str = now.strftime("%H:%M")
    date_str = now.strftime("%d.%m.%Y")
    draw.text((WIDTH - 55, 4), time_str, font=FONT_MED, fill=WHITE)
    draw.text((WIDTH - 80, 20), date_str, font=FONT_TINY, fill=GRAY)
    
    # === SYSTEM STATUS BAR ===
    y = 40
    draw_rounded_rect(draw, (6, y, WIDTH - 6, y + 22), 4, CARD_BG)
    
    # Gateway
    gw_ok = get_gateway_status()
    dot_color = GREEN if gw_ok else RED
    draw.ellipse([12, y + 6, 20, y + 14], fill=dot_color)
    draw.text((23, y + 3), "GW", font=FONT_TINY, fill=GRAY)
    
    # WhatsApp
    wa_ok, wa_status = get_whatsapp_status()
    dot_color = GREEN if wa_ok else RED
    draw.ellipse([60, y + 6, 68, y + 14], fill=dot_color)
    draw.text((71, y + 3), f"WA ({wa_status})", font=FONT_TINY, fill=GRAY)
    
    # System stats
    temp = get_cpu_temp()
    temp_val = float(temp.replace("°C", "")) if "?" not in temp else 0
    temp_color = GREEN if temp_val < 60 else YELLOW if temp_val < 75 else RED
    draw.text((230, y + 3), f"{temp}", font=FONT_TINY, fill=temp_color)
    
    ram = get_memory_usage()
    draw.text((290, y + 3), f"RAM {ram}", font=FONT_TINY, fill=GRAY)
    
    uptime = get_uptime()
    draw.text((360, y + 3), f"Up {uptime}", font=FONT_TINY, fill=GRAY)
    
    # Model
    draw.text((430, y + 3), "S4", font=FONT_TINY, fill=PURPLE)
    
    # === CHILD CARDS ===
    card_w = (WIDTH - 18) // 2
    card_h = 118
    card_y = 66
    
    # Configure your kids here (name, initial, grade, color, workspace)
    render_child_card(draw, 6, card_y, card_w, card_h,
                      "Kid 1", "K", "7", YELLOW, TUTOR_KID1)
    render_child_card(draw, card_w + 12, card_y, card_w, card_h,
                      "Kid 2", "K", "5", BLUE, TUTOR_KID2)
    
    # === EXAMS SECTION ===
    y = 190
    draw_rounded_rect(draw, (6, y, WIDTH - 6, y + 46), 6, CARD_BG)
    draw.text((14, y + 4), "Klassenarbeiten", font=FONT_MED, fill=WHITE)
    
    all_exams = []
    for name, ws in [("Kid 1", TUTOR_KID1), ("Kid 2", TUTOR_KID2)]:
        for exam in read_exams(ws):
            exam["kid"] = name
            all_exams.append(exam)
    
    all_exams.sort(key=lambda e: e["days"])
    
    if all_exams:
        for i, exam in enumerate(all_exams[:2]):
            ey = y + 22 + i * 12
            days = exam["days"]
            if days <= 3:
                day_color = RED
            elif days <= 7:
                day_color = ORANGE
            elif days <= 14:
                day_color = YELLOW
            else:
                day_color = GRAY
            
            draw.text((14, ey), f"{exam['kid']}", font=FONT_TINY, fill=BLUE if exam['kid'] == 'Kid 2' else YELLOW)
            draw.text((60, ey), f"{exam['subject']}", font=FONT_TINY, fill=WHITE)
            draw.text((120, ey), f"{exam['topic'][:20]}", font=FONT_TINY, fill=GRAY)
            draw.text((WIDTH - 80, ey), f"{exam['date']}", font=FONT_TINY, fill=day_color)
            draw.text((WIDTH - 20, ey), f"{days}d", font=FONT_TINY, fill=day_color)
    else:
        draw.text((14, y + 24), "Keine anstehenden Arbeiten", font=FONT_SMALL, fill=DIM)
    
    # === LOG / ACTIVITY ===
    y = 240
    draw_rounded_rect(draw, (6, y, WIDTH - 6, y + 28), 6, CARD_BG)
    draw.text((14, y + 2), "Letzte Aktivitaet", font=FONT_SMALL, fill=GRAY)
    
    try:
        log_date = now.strftime("%Y-%m-%d")
        log_file = f"/tmp/openclaw/openclaw-{log_date}.log"
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                lines = f.readlines()
            for line in reversed(lines[-50:]):
                line = line.strip()
                if any(kw in line.lower() for kw in ["message", "session", "cron", "whatsapp", "error", "tutor"]):
                    if len(line) > 80:
                        line = line[:77] + "..."
                    draw.text((130, y + 3), line, font=FONT_TINY, fill=DIM)
                    break
        else:
            draw.text((130, y + 3), "---", font=FONT_TINY, fill=DIM)
    except:
        draw.text((130, y + 3), "---", font=FONT_TINY, fill=DIM)
    
    # === FOOTER ===
    y = 272 if HEIGHT > 290 else HEIGHT - 22
    draw_rounded_rect(draw, (6, y, WIDTH - 6, y + 18), 4, CARD_BG)
    
    # Backup status
    backup_dir = Path(os.path.expanduser("~/backups/openclaw"))
    try:
        latest = sorted(backup_dir.glob("openclaw-backup-*.tar.gz"))[-1]
        backup_time = datetime.fromtimestamp(latest.stat().st_mtime)
        backup_age = (now - backup_time).total_seconds() / 3600
        if backup_age < 25:
            draw.text((14, y + 4), f"Backup: OK ({backup_time.strftime('%H:%M')})", font=FONT_TINY, fill=GREEN)
        else:
            draw.text((14, y + 4), f"Backup: {int(backup_age)}h alt!", font=FONT_TINY, fill=YELLOW)
    except:
        draw.text((14, y + 4), "Backup: ---", font=FONT_TINY, fill=DIM)
    
    # USB status
    usb_mounted = os.path.ismount("/mnt/backup")
    draw.text((170, y + 4), f"USB: {'OK' if usb_mounted else 'N/A'}", font=FONT_TINY, 
              fill=GREEN if usb_mounted else DIM)
    
    # Agents
    draw.text((240, y + 4), "Agents: 3 (main+2T)", font=FONT_TINY, fill=DIM)
    
    # Update time
    draw.text((WIDTH - 60, y + 4), now.strftime("%H:%M:%S"), font=FONT_TINY, fill=DIM)
    
    return img


def write_to_fb(img):
    """Write PIL image to framebuffer as RGB565"""
    rgb = img.convert("RGB")
    pixels = rgb.load()
    buf = bytearray(WIDTH * HEIGHT * 2)
    
    for y in range(HEIGHT):
        for x in range(WIDTH):
            r, g, b = pixels[x, y]
            rgb565 = ((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3)
            pos = (y * WIDTH + x) * 2
            buf[pos] = rgb565 & 0xFF
            buf[pos + 1] = (rgb565 >> 8) & 0xFF
    
    with open(FB_DEVICE, 'wb') as fb:
        fb.write(buf)


def main():
    print("ClawTutor Mission Control starting...")
    print(f"Display: {WIDTH}x{HEIGHT} on {FB_DEVICE}")
    print(f"Refresh: every {REFRESH_INTERVAL}s")
    
    running = True
    
    def handle_signal(sig, frame):
        nonlocal running
        running = False
        print("\nShutting down dashboard...")
    
    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)
    
    while running:
        try:
            img = render_dashboard()
            write_to_fb(img)
        except Exception as e:
            print(f"Error: {e}")
        
        for _ in range(REFRESH_INTERVAL * 2):
            if not running:
                break
            time.sleep(0.5)
    
    with open(FB_DEVICE, 'wb') as fb:
        fb.write(b'\x00' * WIDTH * HEIGHT * 2)
    print("Dashboard stopped.")


if __name__ == "__main__":
    main()
