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

# Server connection (auto-join when pressing Play)
# Reemplazar por la IP/dominio real del servidor al compilar
SERVER_IP = "TU-SERVIDOR"
SERVER_PORT = "11127"

# Configuration file paths
PROFILES_CONFIG_PATH = os.path.join(MINECRAFT_DIRECTORY, "rp_profiles.json")
SETTINGS_CONFIG_PATH = os.path.join(MINECRAFT_DIRECTORY, "rp_settings.json")