import time
import re
import requests
from bs4 import BeautifulSoup
from pypresence import Presence
import logging
import os
import json
from urllib.parse import quote_plus

# --- Import configuration ---
try:
    from config import (
        CLIENT_ID, MPC_PORT, IGNORE_BRACKETS,
        REPLACE_UNDERSCORES, REPLACE_DOTS,
        LARGE_IMAGE_KEY, SMALL_IMAGE_KEY_PLAYING, SMALL_IMAGE_KEY_PAUSED,
        LARGE_IMAGE_TOOLTIP
    )
except ImportError:
    logging.error("Error: config.py not found. Please create it from the example.")
    exit()

# --- Logging setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Constants ---
MPC_URL = f"http://localhost:{MPC_PORT}/variables.html"
OVERRIDES_FILE = 'overrides.json'
THUMBNAIL_CACHE_FILE = 'thumbnail_cache.json' # New cache file

GARBAGE_PATTERN = re.compile(
    r'\b(1080p|720p|480p|576p|2160p|4k|uhd|bluray|blu-ray|bdrip|dvdrip|hdrip|web-dl|webrip|hdtv|x264|h264|x265|h265|hevc|xvid|ac3|dts|aac|uncensored|remux)\b',
    re.IGNORECASE
)
SERIES_PATTERN = re.compile(r'^(.*?)[\s\._-]*S(\d{1,2})E(\d{1,2})', re.IGNORECASE)
YEAR_PATTERN = re.compile(r'\b(19|20)\d{2}\b')

# --- Helper Functions ---

def load_overrides():
    """Loads the overrides.json file, creating it if it doesn't exist."""
    if not os.path.exists(OVERRIDES_FILE):
        logging.info(f"Creating default '{OVERRIDES_FILE}'.")
        with open(OVERRIDES_FILE, 'w') as f:
            template = {
                "Example Show Name": "https://www.imdb.com/title/tt0944947/",
                "Example Movie Name": "https://i.imgur.com/your_image.jpg"
            }
            json.dump(template, f, indent=4)
        return template
    try:
        with open(OVERRIDES_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        logging.error(f"Error reading or parsing {OVERRIDES_FILE}: {e}. Using no overrides.")
        return {}

# --- New Caching Functions ---
def load_thumbnail_cache():
    """Loads the thumbnail_cache.json file, creating it if it doesn't exist."""
    if not os.path.exists(THUMBNAIL_CACHE_FILE):
        logging.info(f"Creating empty thumbnail cache file: '{THUMBNAIL_CACHE_FILE}'.")
        with open(THUMBNAIL_CACHE_FILE, 'w') as f:
            json.dump({}, f, indent=4)
        return {}
    try:
        with open(THUMBNAIL_CACHE_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        logging.error(f"Error reading or parsing {THUMBNAIL_CACHE_FILE}: {e}. Using empty cache.")
        return {}

def save_thumbnail_cache(cache_data):
    """Saves the given dictionary to the thumbnail cache file."""
    try:
        with open(THUMBNAIL_CACHE_FILE, 'w') as f:
            json.dump(cache_data, f, indent=4)
    except IOError as e:
        logging.error(f"Could not write to thumbnail cache file {THUMBNAIL_CACHE_FILE}: {e}")
# --- End of New Caching Functions ---

def get_display_name(filename):
    """Cleans up a media filename for display, keeping episode titles."""
    name, _ = os.path.splitext(filename)
    match = GARBAGE_PATTERN.search(name)
    if match:
        name = name[:match.start()]
    if IGNORE_BRACKETS:
        name = re.sub(r'\[.*?\]', '', name)
    if REPLACE_UNDERSCORES:
        name = name.replace('_', ' ')
    if REPLACE_DOTS:
        name = name.replace('.', ' ')
    return name.strip().rstrip(' -').strip()

def get_searchable_name(filename):
    """Extracts a clean, searchable name (show/movie title) from a media filename."""
    name, _ = os.path.splitext(filename)
    series_match = SERIES_PATTERN.match(name)
    if series_match:
        name = series_match.group(1)
    else:
        year_match = YEAR_PATTERN.search(name)
        if year_match:
            name = name[:year_match.start()]
    if IGNORE_BRACKETS:
        name = re.sub(r'\[.*?\]', '', name)
    if REPLACE_UNDERSCORES:
        name = name.replace('_', ' ')
    if REPLACE_DOTS:
        name = name.replace('.', ' ')
    return name.strip().rstrip(' -').strip()

def scrape_thumbnail_from_url(imdb_page_url):
    """Scrapes the primary thumbnail from a specific IMDb title page."""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36", "Accept-Language": "en-US,en;q=0.9"}
        media_response = requests.get(imdb_page_url, headers=headers, timeout=5)
        media_response.raise_for_status()
        media_soup = BeautifulSoup(media_response.text, 'lxml')
        image_element = media_soup.select_one('img.ipc-image')
        if image_element and image_element.get('src'):
            thumbnail_url = image_element['src']
            logging.info(f"Scraped thumbnail from {imdb_page_url}")
            return thumbnail_url
        logging.warning(f"Could not find thumbnail on page {imdb_page_url}")
        return None
    except Exception as e:
        logging.error(f"Failed to scrape thumbnail from {imdb_page_url}: {e}")
        return None

def get_imdb_thumbnail(media_name):
    """Searches IMDb and returns the thumbnail URL for the top result."""
    if not media_name:
        return None
    logging.info(f"Searching IMDb for: '{media_name}'")
    try:
        search_url = f"https://www.imdb.com/find?q={quote_plus(media_name)}"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36", "Accept-Language": "en-US,en;q=0.9"}
        search_response = requests.get(search_url, headers=headers, timeout=5)
        search_response.raise_for_status()
        soup = BeautifulSoup(search_response.text, 'lxml')
        result_link = soup.select_one('a.ipc-metadata-list-summary-item__t')
        if not result_link or not result_link.get('href', '').startswith('/title/'):
            logging.warning(f"No valid IMDb search result found for '{media_name}'")
            return None
        media_url = f"https://www.imdb.com{result_link['href']}"
        return scrape_thumbnail_from_url(media_url)
    except Exception as e:
        logging.error(f"An error occurred during IMDb search for '{media_name}': {e}")
        return None

def get_mpc_status():
    """Fetches playback status from MPC-HC's web interface."""
    try:
        response = requests.get(MPC_URL, timeout=2)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        state = int(soup.find('p', {'id': 'state'}).text)
        if state == -1: return None
        return {
            'state': state,
            'filename': os.path.basename(soup.find('p', {'id': 'filepath'}).text),
            'position': sum(int(x) * 60 ** i for i, x in enumerate(reversed(soup.find('p', {'id': 'positionstring'}).text.split(':')))),
            'duration': sum(int(x) * 60 ** i for i, x in enumerate(reversed(soup.find('p', {'id': 'durationstring'}).text.split(':')))),
            'position_string': soup.find('p', {'id': 'positionstring'}).text,
            'duration_string': soup.find('p', {'id': 'durationstring'}).text,
        }
    except requests.RequestException:
        return None
    except (AttributeError, KeyError, ValueError):
        logging.warning("Could not parse MPC-HC data. Is a file fully loaded?")
        return None

def main():
    """Main loop to connect to Discord and update Rich Presence."""
    try:
        rpc = Presence(CLIENT_ID)
        rpc.connect()
        logging.info("Successfully connected to Discord. Monitoring MPC-HC...")
    except Exception as e:
        logging.error(f"Fatal Error: Could not connect to Discord: {e}")
        return

    overrides = load_overrides()
    thumbnail_cache = load_thumbnail_cache() # Load the cache at startup
    last_filename = None
    last_state = -1
    current_thumbnail = LARGE_IMAGE_KEY

    try:
        while True:
            status = get_mpc_status()
            if not status or status['state'] == 0:
                if last_filename is not None:
                    rpc.clear()
                    logging.info("MPC-HC stopped or closed. Clearing presence.")
                    last_filename = None
                    last_state = -1
                    current_thumbnail = LARGE_IMAGE_KEY
                time.sleep(15)
                continue

            if status['filename'] != last_filename or status['state'] != last_state:
                if status['filename'] != last_filename:
                    search_name = get_searchable_name(status['filename'])
                    thumbnail = None

                    # --- MODIFIED: Thumbnail fetching logic with caching ---
                    # 1. Check for a manual override first
                    override_url = overrides.get(search_name)
                    if override_url:
                        logging.info(f"Found manual override for '{search_name}'")
                        if override_url.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                            thumbnail = override_url
                        elif "/title/tt" in override_url:
                            thumbnail = scrape_thumbnail_from_url(override_url)
                        else:
                            logging.warning(f"Invalid override URL for '{search_name}': {override_url}")
                    
                    # 2. If no override, check the cache
                    if not thumbnail:
                        cached_url = thumbnail_cache.get(search_name)
                        if cached_url:
                            logging.info(f"Found cached thumbnail for '{search_name}'")
                            thumbnail = cached_url
                    
                    # 3. If not in overrides or cache, search online
                    if not thumbnail:
                        logging.info(f"No override or cache hit. Searching online for '{search_name}'.")
                        thumbnail = get_imdb_thumbnail(search_name)
                        # 4. If found online, add to cache for next time
                        if thumbnail:
                            logging.info(f"Adding new thumbnail to cache for '{search_name}'")
                            thumbnail_cache[search_name] = thumbnail
                            save_thumbnail_cache(thumbnail_cache)
                    
                    current_thumbnail = thumbnail if thumbnail else LARGE_IMAGE_KEY
                    # --- End of modified logic ---

                last_filename = status['filename']
                last_state = status['state']
                display_details = get_display_name(status['filename'])
                
                payload = {
                    'details': display_details[:128],
                    'large_image': current_thumbnail,
                    'large_text': get_searchable_name(status['filename'])
                }

                if status['state'] == 2:  # Playing
                    logging.info(f"Updating presence: Playing '{display_details}'")
                    payload.update({
                        'small_image': SMALL_IMAGE_KEY_PLAYING, 'small_text': "Playing",
                        'state': "Playing"
                    })
                    if status['duration'] > 0:
                        payload['state'] = f"Playing | {status['duration_string']}"
                        payload['start'] = int(time.time()) - status['position']
                    rpc.clear()
                    time.sleep(1)
                    rpc.update(**payload)
                elif status['state'] == 1:  # Paused
                    logging.info(f"Updating presence: Paused '{display_details}'")
                    payload.update({
                        'state': f"Paused | {status['position_string']} / {status['duration_string']}",
                        'small_image': SMALL_IMAGE_KEY_PAUSED, 'small_text': "Paused"
                    })
                    rpc.update(**payload)
            time.sleep(15)
    except KeyboardInterrupt:
        logging.info("Shutting down...")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}", exc_info=True)
    finally:
        rpc.close()
        logging.info("Connection to Discord closed.")

if __name__ == "__main__":
    if not CLIENT_ID or 'YOUR_DISCORD_CLIENT_ID' in CLIENT_ID:
        logging.error("Please set your CLIENT_ID in config.py before running.")
    else:
        main()