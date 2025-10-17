import os
from api_utils import (
    fetch_character_list,
    fetch_character_details,
    save_character_json,
    download_and_convert_icon_circle,
)

# 🧭 Resolve data folder relative to this script's location
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)  # go up from scripts/
CHARACTERS_DIR = os.path.join(PROJECT_ROOT, "data", "json", "characters")

def check_and_fetch_new_characters():
    os.makedirs(CHARACTERS_DIR, exist_ok=True)

    # Get existing character IDs
    current_ids = {
        int(f[:-5])
        for f in os.listdir(CHARACTERS_DIR)
        if f.endswith(".json") and f[:-5].isdigit()
    }

    # Fetch the latest character list from the API
    latest_list = fetch_character_list()
    latest_ids = {c["Id"] for c in latest_list}

    # Determine which characters are new
    new_ids = latest_ids - current_ids
    if not new_ids:
        print("✅ No new characters found.")
        return False

    print(f"✨ Found {len(new_ids)} new characters: {new_ids}")

    # Fetch details and icons for new characters
    for character in latest_list:
        if character["Id"] not in new_ids:
            continue
        char_id = character["Id"]
        print(f"Fetching new character {character['Name']} (ID {char_id})...")
        details = fetch_character_details(char_id)
        save_character_json(details)

        icon_url = details.get("RoleHeadIconCircle")
        if icon_url:
            full_icon_url = (
                f"https://api-v2.encore.moe{icon_url}" if icon_url.startswith("/") else icon_url
            )
            download_and_convert_icon_circle(full_icon_url, char_id)

    return True

if __name__ == "__main__":
    check_and_fetch_new_characters()