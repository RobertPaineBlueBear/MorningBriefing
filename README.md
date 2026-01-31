# Morning Briefing

A Python desktop app that greets you each morning with today's weather, calendar events, and a motivational quote. Launches automatically when you log into your Mac.

## Features

- **Weather** - Current temperature, high/low, and conditions for Austin, TX (via [Open-Meteo](https://open-meteo.com/) - no API key required)
- **Calendar Events** - Pulls today's events from macOS Calendar (via `icalBuddy` or AppleScript)
- **Motivational Quote** - A random quote to start your day
- **Dark-themed GUI** - Clean `tkinter` window, easy to read

## Requirements

- macOS
- Python 3.8+
- `tkinter` (included with Python on macOS)
- Internet connection (for weather data)

## Quick Start

```bash
# Clone the repo
git clone <repo-url> && cd MorningBriefing

# Run setup (installs deps + configures auto-launch on login)
bash setup.sh
```

That's it. The briefing will appear next time you log in.

To test it immediately:

```bash
python3 morning_briefing.py
```

## Calendar Integration

The app tries two methods to read your macOS Calendar:

1. **icalBuddy** (recommended) - Install with `brew install ical-buddy`
2. **AppleScript fallback** - Works out of the box but may prompt for Calendar access permission

If neither is available, the app will show "No events today."

## Customization

Edit the constants at the top of `morning_briefing.py`:

| Variable    | Description                      | Default           |
|-------------|----------------------------------|--------------------|
| `CITY`      | City name shown in the header    | `"Austin"`         |
| `LATITUDE`  | Latitude for weather API         | `30.2672`          |
| `LONGITUDE` | Longitude for weather API        | `-97.7431`         |

## Uninstall

```bash
bash uninstall.sh
```

This removes the auto-launch configuration. The app files remain in place so you can re-run `setup.sh` later.

## File Structure

```
MorningBriefing/
  morning_briefing.py       # Main application
  requirements.txt          # Python dependencies
  setup.sh                  # Install + enable auto-launch
  uninstall.sh              # Disable auto-launch
  com.morningbriefing.plist # LaunchAgent template
  README.md
```
