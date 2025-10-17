import os
import json
import requests
from PIL import Image
from io import BytesIO

BASE_URL = "https://api-v2.encore.moe/en/character"

# Output directories
# 🧭 Resolve data folder relative to this script's location
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)  # go up from scripts/
CHARACTERS_DIR = os.path.join(PROJECT_ROOT, "data", "json", "characters")
ICON_CIRCLE_DIR = os.path.join(PROJECT_ROOT, "data", "imgs", "iconCircle")

def fetch_json(url: str):
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def fetch_character_list():
    """Fetch and return the character list from the API."""
    data = fetch_json(BASE_URL)
    return data.get("roleList", [])

def fetch_character_details(char_id: int):
    """Fetch and return full character data for a given ID."""
    url = f"{BASE_URL}/{char_id}"
    return fetch_json(url)

def save_character_json(character_data: dict):
    """Save character JSON to data/json/characters."""
    os.makedirs(CHARACTERS_DIR, exist_ok=True)
    char_id = character_data.get("Id")
    filename = f"{char_id}.json"
    filepath = os.path.join(CHARACTERS_DIR, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(character_data, f, indent=2, ensure_ascii=False)
    return filepath

def download_and_convert_icon_circle(url: str, char_id: int):
    """Download RoleHeadIconCircle image and convert to WebP."""
    if not url:
        return
    os.makedirs(ICON_CIRCLE_DIR, exist_ok=True)
    response = requests.get(url)
    if response.status_code != 200:
        print(f"⚠️ Failed to fetch icon for {char_id}")
        return

    try:
        img = Image.open(BytesIO(response.content))
        output_path = os.path.join(ICON_CIRCLE_DIR, f"{char_id}.webp")
        img.save(output_path, "WEBP")
        print(f"🖼️ Saved iconCircle: {output_path}")
    except Exception as e:
        print(f"❌ Failed to convert icon for {char_id}: {e}")

def fetch_and_save_all_characters():
    """Fetch all characters, save their JSON, and download icons."""
    role_list = fetch_character_list()
    print(f"Found {len(role_list)} characters")

    for role in role_list:
        char_id = role["Id"]
        char_name = role["Name"]
        print(f"Fetching {char_name} (ID {char_id})...")
        details = fetch_character_details(char_id)
        save_character_json(details)

        # Download RoleHeadIconCircle
        icon_url = details.get("RoleHeadIconCircle")
        if icon_url:
            full_icon_url = f"https://api-v2.encore.moe{icon_url}" if icon_url.startswith("/") else icon_url
            download_and_convert_icon_circle(full_icon_url, char_id)
