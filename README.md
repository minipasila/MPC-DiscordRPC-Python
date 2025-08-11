# MPC-DiscordRPC (Python Edition)
Discord Rich Presence for Media Player Classic (Home Cinema and Black Edition) with enhanced features

![Media Player Classic Home Cinema and Black Edition Rich Presence on Discord](https://i.imgur.com/QAAJZgL.png)

## ✨ Features

- **Automatic IMDb Thumbnails**: Fetches movie/show posters from IMDb automatically
- **Smart Thumbnail Caching**: Reduces API calls by caching thumbnails locally
- **Manual Overrides**: Customize thumbnails and IMDb links for specific content
- **Intelligent Filename Cleaning**: Advanced detection and removal of quality tags, release groups, and other clutter
- **Episode Detection**: Properly handles TV series with season/episode formatting
- **Real-time Status Updates**: Shows play/pause status and progress

## How does this work?

This Python program fetches playback data from MPC-HC/MPC-BE's Web Interface and displays it in your Discord profile through Discord's Rich Presence API. It automatically searches IMDb for thumbnails and intelligently cleans filenames for better presentation.

**Note**: This only works with the [Discord desktop client](https://discordapp.com/download), not the web app.

## Prerequisites

1. **Discord Application Setup**:
   - Go to [Discord Developer Portal](https://discord.com/developers/applications)
   - Create a new application (the name will appear as "Playing [YourAppName]")
   - Copy your **Client ID** from the OAuth2 section
   - Optionally, upload custom icons in Rich Presence → Art Assets

2. **Python Installation**:
   - Install [Python 3.7+](https://www.python.org/downloads/)
   - Make sure to check "Add Python to PATH" during installation

## Installation

### Step 1: Enable MPC Web Interface

Open Media Player Classic, go to `View > Options > Player > Web Interface` and enable `Listen on port:`. The default port is `13579`.

![Enable the option "Listen on port"](https://cdn.discordapp.com/attachments/416273308540207116/428748994307424256/unknown.png)

### Step 2: Download and Setup

1. [Download this project as a .zip file](https://github.com/minipasila/MPC-DiscordRPC-Python/archive/main.zip) and extract it, or clone with Git:

```bash
git clone https://github.com/minipasila/MPC-DiscordRPC-Python.git
cd MPC-DiscordRPC-Python
```

2. Install required Python packages:

```bash
pip install -r requirements.txt
```

### Step 3: Configuration

1. Open `config.py` in a text editor
2. Replace `CLIENT_ID = '1398017215390814339'` with your Discord application's Client ID
3. Adjust other settings as needed (see [Configuration Options](#configuration-options) below)

### Step 4: Run the Program

```bash
python main.py
```

The program will start monitoring MPC and updating your Discord status automatically. Keep the terminal window open while using.

## Configuration Options

Edit `config.py` to customize behavior:

### Discord Settings
- **`CLIENT_ID`**: Your Discord application's Client ID (required)
- **`LARGE_IMAGE_KEY`**: Fallback icon when IMDb thumbnails aren't available
- **`SMALL_IMAGE_KEY_PLAYING/PAUSED`**: Icons for play/pause status
- **`LARGE_IMAGE_TOOLTIP`**: Hover text for the main image

### MPC Settings
- **`MPC_PORT`**: Port for MPC Web Interface (default: 13579)

### Display Settings
- **`CLEAN_FILENAMES_ADVANCED`**: Intelligently removes quality tags like "1080p", "BluRay", etc.
- **`IGNORE_BRACKETS`**: Removes content in square brackets `[like this]`
- **`REPLACE_UNDERSCORES`**: Converts underscores to spaces
- **`REPLACE_DOTS`**: Converts dots to spaces (less aggressive than advanced cleaning)

## Advanced Features

### Custom Thumbnails and Overrides

The program creates an `overrides.json` file where you can specify custom thumbnails or IMDb pages:

```json
{
    "Your Favorite Show": "https://www.imdb.com/title/tt1234567/",
    "Some Movie": "https://i.imgur.com/custom_image.jpg"
}
```

- **IMDb URLs**: Program will scrape the poster from the IMDb page
- **Direct Image URLs**: Must end with `.jpg`, `.jpeg`, `.png`, or `.webp`

### Thumbnail Caching

The program automatically caches IMDb thumbnails in `thumbnail_cache.json` to reduce repeated searches and improve performance. The cache persists between restarts.

## Updating

1. Stop the program (Ctrl+C in terminal)
2. Download the latest version or run `git pull` if using Git
3. Install any new dependencies: `pip install -r requirements.txt`
4. Restart with `python main.py`

## Troubleshooting

### Common Issues

**"Could not connect to Discord"**
- Make sure Discord desktop app is running
- Check that your `CLIENT_ID` is correct
- Try restarting Discord

**"Could not parse MPC-HC data"**
- Ensure MPC Web Interface is enabled on the correct port
- Make sure a media file is fully loaded (not just opened)
- Check that `MPC_PORT` in config.py matches your MPC settings

**No thumbnails appearing**
- Check your internet connection
- IMDb may be temporarily blocking requests - thumbnails will resume automatically
- You can add manual overrides in `overrides.json`

### Logs and Debugging

The program outputs detailed logs to help diagnose issues. Look for error messages in the terminal output.

## Files Created

- `overrides.json`: Manual thumbnail and IMDb overrides
- `thumbnail_cache.json`: Cached IMDb thumbnails for faster loading