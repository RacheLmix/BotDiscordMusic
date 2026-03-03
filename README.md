# Shoko Singer – Discord Music Bot

Shoko Singer is a Discord music bot built with discord.py, Wavelink, and Lavalink.
It supports both prefix commands and slash commands, interactive player controls, queue management, and basic cooldown handling.

---

## Features

* Play music via song name or URL
* Queue system with auto-play next
* Pause / Resume
* Skip
* Stop and clear queue
* Interactive button controls
* Automatic track end handling
* Basic cooldown protection
* Voice auto-connect
* Global slash command sync

---

## Tech Stack

* Python 3.10+
* discord.py (commands + app_commands)
* Wavelink (Lavalink client)
* Lavalink server
* AsyncIO

---

## Installation

### 1. Clone repository

```bash
git clone https://github.com/yourusername/ShokoSinger.git
cd ShokoSinger
```

---

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

If no requirements file:

```bash
pip install discord.py wavelink
```

---

### 3. Setup Environment Variables

Create a `.env` file in the root directory:

```
TOKEN=your_discord_bot_token_here
```

Or set environment variable manually:

Windows (PowerShell):

```powershell
setx TOKEN "your_token_here"
```

Restart the terminal after setting.

---

## Running Lavalink

This bot requires a Lavalink server running locally.

Example:

```bash
java -jar /LavaLink/Lavalink.jar
```

Default configuration used in code:

```
URI: http://127.0.0.1:8080
Password: 292005 <Custom Pass>
```

Make sure your `application.yml` in Lavalink matches this password.

---

## Run the Bot

```bash
python main.py
```

If everything is correct, you should see:

```
Logged in as <BotName>
Lavalink connected
Synced X global slash commands
```

---

## Commands

### Prefix Commands

| Command           | Description        |
| ----------------- | ------------------ |
| Shoko join        | Join voice channel |
| Shoko play <song> | Play music         |
| Shoko queue       | Show queue         |
| Shoko leave       | Leave voice        |

---

### Slash Commands

* /join
* /play
* /list
* /skip
* /pause
* /resume
* /stop
* /leave

---

## How It Works

* Uses wavelink.Node to connect to Lavalink
* Maintains per-guild queues using defaultdict
* Automatically plays next track on on_wavelink_track_end
* Interactive player controls implemented with discord.ui.View
* Simple cooldown system to prevent spam

---

## Security Notes

* Never hardcode your bot token
* Always use environment variables
* Reset token immediately if exposed
* Do not commit `.env` to GitHub

---

## Future Improvements

* Volume control
* Shuffle mode
* Loop mode
* Persistent queue
* Better error handling
* Music filters
* Database support
* Docker deployment

---

## License

This project is for educational purposes.

---

## Author

Created for learning and experimenting with Discord bot development and audio streaming systems.
