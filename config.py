# config.py

# --- Discord Application Settings ---
# This is REQUIRED. Create an application at https://discord.com/developers/applications
# The name of your application here is what shows as "Playing AppName".
# Go to "OAuth2" to find your "CLIENT ID" and paste it here.
CLIENT_ID = '1398017215390814339'  # Replace with your own Client ID

# --- MPC-HC Settings ---
MPC_PORT = 13579

# --- Rich Presence Display Settings ---
# Upload these assets in your Discord App -> Rich Presence -> Art Assets
# NOTE: The large image key is now a FALLBACK for when an IMDb thumbnail cannot be found.
LARGE_IMAGE_KEY = 'mpc_logo_large'      # Key for the large MPC-HC icon
SMALL_IMAGE_KEY_PLAYING = 'play_icon'   # Key for the small 'play' icon
SMALL_IMAGE_KEY_PAUSED = 'pause_icon'   # Key for the small 'pause' icon

# The text that appears when you hover over the large thumbnail.
LARGE_IMAGE_TOOLTIP = "Media Player Classic - Home Cinema"


# --- String Manipulation Settings ---

# Set to True to intelligently remove quality/source tags (e.g., "1080p", "BluRay", "x264").
CLEAN_FILENAMES_ADVANCED = True

# Set to True to remove content in square brackets, e.g., [1080p] or [CRC32]
IGNORE_BRACKETS = True

# Set to True to replace underscores with spaces
REPLACE_UNDERSCORES = True

# Set to True to replace periods with spaces (the advanced cleaner is better for this)
REPLACE_DOTS = True