import os
import re
import json
import requests
from typing import List, Optional, Union

LANG_KEYS = {
    "VoiceEn": "en",
    "VoiceJa": "ja",
    "VoiceKo": "ko",
    "VoiceZh": "zh"
}

# 🧭 Resolve data folder relative to this script's location
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)  # go up from scripts/
VOICES_DIR = os.path.join(PROJECT_ROOT, "voices")  # Keep voices at root for direct serving

def matches_filter(title: str, filters: List[str], character_name: str) -> bool:
    if not filters:
        return False
    normalized_title = title.lower().strip()
    normalized_title = re.sub(r"[\u2019']", "", normalized_title)  # ’ and '
    normalized_title = re.sub(r"[:\u2013-]", "", normalized_title)  # en dash + hyphen
    normalized_title = re.sub(r"\s+", " ", normalized_title)
    parts = normalized_title.split(" ", 1)
    suffix = parts[1] if len(parts) > 1 else normalized_title
    for f in filters:
        filter_str = f.replace("{character}", character_name).lower().strip()
        filter_str = re.sub(r"[\u2019']", "", filter_str)
        if normalized_title.startswith(filter_str): 
            return True
        if suffix == filter_str or suffix.startswith(filter_str): 
            return True
        if filter_str in normalized_title: 
            return True
    return False

def parse_sort_filters(sort_filters: List[Union[str, int]]):
    parsed_ranges = []
    for sf in sort_filters:
        if isinstance(sf, int):
            parsed_ranges.append(range(sf, sf + 1))
        elif isinstance(sf, str):
            sf = sf.strip()
            if "-" in sf:
                start, end = sf.split("-", 1)
                if start.isdigit() and end.isdigit():
                    parsed_ranges.append(range(int(start), int(end) + 1))
            elif sf.isdigit():
                num = int(sf)
                parsed_ranges.append(range(num, num + 1))
    return parsed_ranges

def matches_sort(sort_value: int, ranges: list[range]) -> bool:
    for r in ranges:
        if sort_value in r:
            return True
    return False

def download_voice_lines(json_path: str, 
                         filters: Optional[List[str]] = None,
                         sort_filters: Optional[List[Union[str, int]]] = None):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    voice_entries = data.get("VoiceList", [])
    if not voice_entries:
        return

    character_name = data.get("Name", {}).get("Content", "").lower()
    role_id = str(data.get("Id", "unknown"))
    output_dir = os.path.join(VOICES_DIR, role_id)
    os.makedirs(output_dir, exist_ok=True)
    parsed_sort_ranges = parse_sort_filters(sort_filters or [])

    print(f"🎧 {character_name.title()} (ID: {role_id})")

    for entry in voice_entries:
        voice_id = entry.get("Id")
        title = entry.get("VoiceTitle", "")
        sort_value = entry.get("Sort")
        title_match = matches_filter(title, filters or [], character_name)
        sort_match = matches_sort(sort_value, parsed_sort_ranges) if sort_value is not None else False

        if not (title_match or sort_match or (not filters and not sort_filters)):
            continue

        for lang_key, lang_code in LANG_KEYS.items():
            url = entry.get(lang_key)
            if url:
                filename = f"{voice_id}_{lang_code}.mp3"
                file_path = os.path.join(output_dir, filename)
                try:
                    r = requests.get(url, timeout=10)
                    r.raise_for_status()
                    with open(file_path, "wb") as f:
                        f.write(r.content)
                    print(f"✅ [{sort_value}] {title} ({lang_code})")
                except Exception as e:
                    print(f"❌ Failed [{sort_value}] {title} ({lang_code}): {e}")
