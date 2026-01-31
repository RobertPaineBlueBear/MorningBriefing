#!/usr/bin/env python3
"""
Morning Briefing App
Displays today's weather, calendar events, and a motivational quote
in a clean GUI window. Designed to launch on macOS startup.
"""

import datetime
import json
import os
import random
import tkinter as tk
from tkinter import font as tkfont

import requests
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# ── Configuration ────────────────────────────────────────────────────────────
CITY = "Austin"
LATITUDE = 30.2672
LONGITUDE = -97.7431
WINDOW_WIDTH = 520
WINDOW_HEIGHT = 640

# ── Google Calendar (read-only) ─────────────────────────────────────────────
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_FILE = os.path.join(_DIR, "credentials.json")
TOKEN_FILE = os.path.join(_DIR, "token.json")

# ── Colors & Style ───────────────────────────────────────────────────────────
BG = "#1e1e2e"
FG = "#cdd6f4"
ACCENT = "#89b4fa"
SECTION_BG = "#313244"
MUTED = "#a6adc8"
QUOTE_FG = "#f5c2e7"

MOTIVATIONAL_QUOTES = [
    ("The secret of getting ahead is getting started.", "Mark Twain"),
    ("It is never too late to be what you might have been.", "George Eliot"),
    ("Act as if what you do makes a difference. It does.", "William James"),
    ("Success is not final, failure is not fatal: it is the courage to continue that counts.", "Winston Churchill"),
    ("Believe you can and you're halfway there.", "Theodore Roosevelt"),
    ("The only way to do great work is to love what you do.", "Steve Jobs"),
    ("In the middle of every difficulty lies opportunity.", "Albert Einstein"),
    ("What you get by achieving your goals is not as important as what you become by achieving your goals.", "Zig Ziglar"),
    ("Start where you are. Use what you have. Do what you can.", "Arthur Ashe"),
    ("You are never too old to set another goal or to dream a new dream.", "C.S. Lewis"),
    ("Everything you've ever wanted is on the other side of fear.", "George Addair"),
    ("Don't watch the clock; do what it does. Keep going.", "Sam Levenson"),
    ("The best time to plant a tree was 20 years ago. The second best time is now.", "Chinese Proverb"),
    ("Your limitation—it's only your imagination.", "Unknown"),
    ("Great things never come from comfort zones.", "Unknown"),
    ("Dream it. Wish it. Do it.", "Unknown"),
    ("The harder you work for something, the greater you'll feel when you achieve it.", "Unknown"),
    ("Do something today that your future self will thank you for.", "Sean Patrick Flanery"),
    ("Little things make big days.", "Unknown"),
    ("It's going to be hard, but hard does not mean impossible.", "Unknown"),
]

WMO_WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Foggy",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snow",
    73: "Moderate snow",
    75: "Heavy snow",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}

WEATHER_ICONS = {
    0: "\u2600",      # ☀ Clear
    1: "\U0001f324",   # 🌤 Mainly clear
    2: "\u26c5",       # ⛅ Partly cloudy
    3: "\u2601",       # ☁ Overcast
    45: "\U0001f32b",  # 🌫 Fog
    48: "\U0001f32b",  # 🌫 Fog
    51: "\U0001f326",  # 🌦 Drizzle
    53: "\U0001f326",  # 🌦 Drizzle
    55: "\U0001f326",  # 🌦 Drizzle
    61: "\U0001f327",  # 🌧 Rain
    63: "\U0001f327",  # 🌧 Rain
    65: "\U0001f327",  # 🌧 Rain
    71: "\U0001f328",  # 🌨 Snow
    73: "\U0001f328",  # 🌨 Snow
    75: "\U0001f328",  # 🌨 Snow
    80: "\U0001f326",  # 🌦 Showers
    81: "\U0001f327",  # 🌧 Showers
    82: "\U0001f327",  # 🌧 Showers
    95: "\u26c8",      # ⛈ Thunderstorm
    96: "\u26c8",      # ⛈ Thunderstorm
    99: "\u26c8",      # ⛈ Thunderstorm
}


# ── Data Fetching ────────────────────────────────────────────────────────────

def fetch_weather():
    """Fetch today's weather from Open-Meteo (free, no API key needed)."""
    try:
        url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={LATITUDE}&longitude={LONGITUDE}"
            f"&daily=temperature_2m_max,temperature_2m_min,weathercode"
            f"&current_weather=true"
            f"&temperature_unit=fahrenheit"
            f"&timezone=America%2FChicago"
        )
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        current = data["current_weather"]
        daily = data["daily"]

        temp_now = current["temperature"]
        code = current["weathercode"]
        high = daily["temperature_2m_max"][0]
        low = daily["temperature_2m_min"][0]
        description = WMO_WEATHER_CODES.get(code, "Unknown")
        icon = WEATHER_ICONS.get(code, "")

        return {
            "temp": temp_now,
            "high": high,
            "low": low,
            "description": description,
            "icon": icon,
        }
    except Exception as e:
        return {"error": str(e)}


def _get_google_calendar_credentials():
    """Load or create Google Calendar OAuth credentials (read-only)."""
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                return None
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES
            )
            print("\n" + "=" * 60)
            print("Open the link below in your browser to authorize")
            print("read-only access to Google Calendar.")
            print("=" * 60)
            creds = flow.run_local_server(
                port=0,
                open_browser=False,
                authorization_prompt_message="\n  {url}\n",
            )
            print("Authorization complete!\n")
        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())
    return creds


def fetch_calendar_events():
    """
    Fetch today's calendar events from Google Calendar (read-only).
    Returns a list of formatted event strings.
    """
    try:
        creds = _get_google_calendar_credentials()
        if creds is None:
            return ["(credentials.json not found \u2014 see README)"]

        service = build("calendar", "v3", credentials=creds)

        today = datetime.date.today()
        time_min = datetime.datetime.combine(
            today, datetime.time.min
        ).isoformat() + "Z"
        time_max = datetime.datetime.combine(
            today, datetime.time.max
        ).isoformat() + "Z"

        result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )

        events = []
        for item in result.get("items", []):
            start = item["start"].get("dateTime", item["start"].get("date", ""))
            summary = item.get("summary", "(No title)")
            if "T" in start:
                dt = datetime.datetime.fromisoformat(start)
                time_str = dt.strftime("%-I:%M %p")
                events.append(f"\u2022 {time_str} - {summary}")
            else:
                events.append(f"\u2022 All day - {summary}")
        return events
    except Exception as e:
        return [f"(Calendar error: {e})"]


def get_quote():
    """Return a random motivational quote."""
    text, author = random.choice(MOTIVATIONAL_QUOTES)
    return text, author


# ── GUI ──────────────────────────────────────────────────────────────────────

class MorningBriefingApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Morning Briefing")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)

        # Center window on screen
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        x = (screen_w - WINDOW_WIDTH) // 2
        y = (screen_h - WINDOW_HEIGHT) // 3
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x}+{y}")

        # Fonts
        self.font_title = tkfont.Font(family="Helvetica Neue", size=22, weight="bold")
        self.font_section = tkfont.Font(family="Helvetica Neue", size=14, weight="bold")
        self.font_body = tkfont.Font(family="Helvetica Neue", size=12)
        self.font_small = tkfont.Font(family="Helvetica Neue", size=10)
        self.font_temp = tkfont.Font(family="Helvetica Neue", size=36, weight="bold")
        self.font_quote = tkfont.Font(family="Helvetica Neue", size=12, slant="italic")
        self.font_icon = tkfont.Font(size=40)

        self._build_ui()

    def _build_ui(self):
        root = self.root
        today = datetime.date.today()
        day_str = today.strftime("%A, %B %-d, %Y")

        # ── Header ───────────────────────────────────────────────────────
        header = tk.Frame(root, bg=BG)
        header.pack(fill="x", padx=24, pady=(20, 4))

        tk.Label(
            header, text="Good Morning", font=self.font_title, bg=BG, fg=FG
        ).pack(anchor="w")

        tk.Label(
            header, text=day_str, font=self.font_small, bg=BG, fg=MUTED
        ).pack(anchor="w", pady=(2, 0))

        # ── Weather Section ──────────────────────────────────────────────
        weather_frame = tk.Frame(root, bg=SECTION_BG, highlightthickness=0)
        weather_frame.pack(fill="x", padx=24, pady=(16, 0), ipady=12)

        tk.Label(
            weather_frame,
            text=f"\u2601  Weather \u2014 {CITY}",
            font=self.font_section,
            bg=SECTION_BG,
            fg=ACCENT,
        ).pack(anchor="w", padx=16, pady=(8, 0))

        weather = fetch_weather()
        if "error" in weather:
            tk.Label(
                weather_frame,
                text=f"Could not load weather: {weather['error']}",
                font=self.font_body,
                bg=SECTION_BG,
                fg=MUTED,
                wraplength=WINDOW_WIDTH - 80,
                justify="left",
            ).pack(anchor="w", padx=16, pady=(4, 8))
        else:
            row = tk.Frame(weather_frame, bg=SECTION_BG)
            row.pack(fill="x", padx=16, pady=(4, 0))

            tk.Label(
                row,
                text=weather["icon"],
                font=self.font_icon,
                bg=SECTION_BG,
                fg=FG,
            ).pack(side="left", padx=(0, 8))

            temp_col = tk.Frame(row, bg=SECTION_BG)
            temp_col.pack(side="left")

            tk.Label(
                temp_col,
                text=f"{weather['temp']:.0f}\u00b0F",
                font=self.font_temp,
                bg=SECTION_BG,
                fg=FG,
            ).pack(anchor="w")

            tk.Label(
                temp_col,
                text=weather["description"],
                font=self.font_body,
                bg=SECTION_BG,
                fg=MUTED,
            ).pack(anchor="w")

            tk.Label(
                weather_frame,
                text=f"High: {weather['high']:.0f}\u00b0F   Low: {weather['low']:.0f}\u00b0F",
                font=self.font_small,
                bg=SECTION_BG,
                fg=MUTED,
            ).pack(anchor="w", padx=16, pady=(2, 8))

        # ── Calendar Section ─────────────────────────────────────────────
        cal_frame = tk.Frame(root, bg=SECTION_BG, highlightthickness=0)
        cal_frame.pack(fill="x", padx=24, pady=(16, 0), ipady=12)

        tk.Label(
            cal_frame,
            text="\U0001f4c5  Today's Events",
            font=self.font_section,
            bg=SECTION_BG,
            fg=ACCENT,
        ).pack(anchor="w", padx=16, pady=(8, 4))

        events = fetch_calendar_events()
        if events:
            for event in events:
                tk.Label(
                    cal_frame,
                    text=event,
                    font=self.font_body,
                    bg=SECTION_BG,
                    fg=FG,
                    wraplength=WINDOW_WIDTH - 80,
                    justify="left",
                    anchor="w",
                ).pack(anchor="w", padx=16, pady=(2, 0))
        else:
            tk.Label(
                cal_frame,
                text="No events today \u2014 enjoy your free day!",
                font=self.font_body,
                bg=SECTION_BG,
                fg=MUTED,
            ).pack(anchor="w", padx=16, pady=(4, 0))

        # Pad the bottom of calendar
        tk.Frame(cal_frame, bg=SECTION_BG, height=8).pack()

        # ── Quote Section ────────────────────────────────────────────────
        quote_frame = tk.Frame(root, bg=SECTION_BG, highlightthickness=0)
        quote_frame.pack(fill="x", padx=24, pady=(16, 0), ipady=12)

        tk.Label(
            quote_frame,
            text="\u2728  Daily Motivation",
            font=self.font_section,
            bg=SECTION_BG,
            fg=ACCENT,
        ).pack(anchor="w", padx=16, pady=(8, 4))

        text, author = get_quote()
        tk.Label(
            quote_frame,
            text=f"\u201c{text}\u201d",
            font=self.font_quote,
            bg=SECTION_BG,
            fg=QUOTE_FG,
            wraplength=WINDOW_WIDTH - 80,
            justify="left",
        ).pack(anchor="w", padx=16, pady=(4, 0))

        tk.Label(
            quote_frame,
            text=f"\u2014 {author}",
            font=self.font_small,
            bg=SECTION_BG,
            fg=MUTED,
        ).pack(anchor="w", padx=32, pady=(2, 8))

        # ── Dismiss Button ───────────────────────────────────────────────
        btn = tk.Button(
            root,
            text="Have a great day!",
            font=self.font_body,
            bg=ACCENT,
            fg=BG,
            activebackground="#b4d0fb",
            activeforeground=BG,
            relief="flat",
            cursor="hand2",
            command=self.root.destroy,
            padx=20,
            pady=6,
        )
        btn.pack(pady=(20, 16))

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = MorningBriefingApp()
    app.run()
