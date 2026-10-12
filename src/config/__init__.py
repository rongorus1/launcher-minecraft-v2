import os

from helpers.system_tools import get_launcher_directory

# Global variables
LAUNCHER_NAME = "RongonLang Launcher"
LAUNCHER_DIR = get_launcher_directory()
MINECRAFT_DIRECTORY = os.path.join(LAUNCHER_DIR, ".minecraft")
os.makedirs(MINECRAFT_DIRECTORY, exist_ok=True)

# Minecraft and Forge configuration
MINECRAFT_VERSION = "1.20.1"
FORGE_VERSION = "47.4.0"

# Modpack distribution: release de GitHub con manifest.json + overrides/
MODPACK_REPO = "rongorus1/Panas-RPG-Optimzed-1.20.1"
MODPACK_ASSET_PREFIX = "Panas.RPG."

# Configuration file paths
PROFILES_CONFIG_PATH = os.path.join(MINECRAFT_DIRECTORY, "rp_profiles.json")
SETTINGS_CONFIG_PATH = os.path.join(MINECRAFT_DIRECTORY, "rp_settings.json")