import json
import os
import requests
from PIL import Image
from io import BytesIO

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)  # go up from scripts/
CHARACTERS_JSON_DIR = os.path.join(PROJECT_ROOT, "data", "json", "characters")
CHARACTERS_PATH = os.path.join(PROJECT_ROOT, "data", "json", "characters.json")
ICON_WEEKLY_BOOS_DIR = os.path.join(PROJECT_ROOT, "data", "imgs", "iconWeeklyBoss")
ICON_ASCENSION_DIR = os.path.join(PROJECT_ROOT, "data", "imgs", "iconAscension")

def download_and_convert_icon(dir_path, url: str, icon_id: int):
    if not url:
        return
    os.makedirs(dir_path, exist_ok=True)
    if os.path.exists(os.path.join(dir_path, f"{icon_id}.webp")): 
        return
    response = requests.get(url)
    if response.status_code != 200:
        print(f"⚠️ Failed to fetch icon for {icon_id}")
        return

    try:
        img = Image.open(BytesIO(response.content))
        output_path = os.path.join(dir_path, f"{icon_id}.webp")
        img.save(output_path, "WEBP")
    except Exception as e:
        print(f"❌ Failed to convert icon for {icon_id}: {e}")

def fix_filename(path):
    base = path.split('/')[-1].split('.')[0]  # Extract filename before the dot
    return f"{path.rsplit('.', 1)[0].rsplit('/', 1)[0]}/{base}.png"

def create_characters_json(characters_dir, characters_path):
    characters_list = []
    with open(characters_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    for character in data:
        character_id = character['id'] if isinstance(character['id'], int) else min(character['id'])

        with open(os.path.join(characters_dir, f"{character_id}.json"), "r", encoding="utf-8") as f:
             character_file = json.load(f)

        weekly_id = character_file['Skills'][0]['Consumes'][-1]['Consume'][-2]['Key']
        weekly_icon = character_file['Skills'][0]['Consumes'][-1]['Consume'][-2]['Icon']
        for ascension_step in character_file['Breaches']:
            if ascension_step['MaxLevel'] == 90:
                ascension_id = ascension_step["Items"][0]['Key']
                ascension_icon = ascension_step["Items"][0]['Icon']

        updated_dict = {
            'id': character['id'],
            'name': character['name'],
            'star': character['star'],
            'element': character['element'],
            'weapon': character['weapon'],
            'gender': character['gender'],
            'region': character['region'],
            'influence': character['influence'],
            'affiliation': character['affiliation'],
            'bonusStats': character['bonusStats'],
            'debut': character['debut'],
            'upgrade': {'ascension': ascension_id, 'skill': weekly_id}
        }
        download_and_convert_icon(ICON_ASCENSION_DIR, f"https://api-v2.encore.moe/resource/Data{fix_filename(ascension_icon)}", ascension_id)
        download_and_convert_icon(ICON_WEEKLY_BOOS_DIR, f"https://api-v2.encore.moe/resource/Data{fix_filename(weekly_icon)}", weekly_id)
        print(updated_dict)
        characters_list.append(updated_dict)
    with open(characters_path, "w", encoding="utf-8") as f:
        json.dump(characters_list, f, ensure_ascii=False, indent=2)


create_characters_json(CHARACTERS_JSON_DIR, CHARACTERS_PATH)