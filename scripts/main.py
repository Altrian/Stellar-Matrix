import os
import glob
import sys
from check_new_characters import check_and_fetch_new_characters
from voice_downloader import download_voice_lines
from manifest_generator import generate_manifest

CHARACTERS_JSON_DIR = "data/json/characters"

# 1. Check for new characters
has_new_characters = check_and_fetch_new_characters()

# 2. Download voices only if needed
if has_new_characters:
    for path in glob.glob(f"{CHARACTERS_JSON_DIR}/*.json"):
        download_voice_lines(
            path,
            filters=["Resonance Liberation", "Trouble", "Hobby"],
            sort_filters=["1-5", 8, "12-14"]
        )

# 3. Generate manifest
manifest_path = "data/json/manifest.json"
before_hash = None
if os.path.exists(manifest_path):
    with open(manifest_path, "rb") as f:
        import hashlib
        before_hash = hashlib.sha256(f.read()).hexdigest()

generate_manifest()

# 4. Check if manifest changed
after_hash = None
if os.path.exists(manifest_path):
    with open(manifest_path, "rb") as f:
        after_hash = hashlib.sha256(f.read()).hexdigest()

manifest_changed = before_hash != after_hash

# 5. Decide whether to skip
if not has_new_characters and not manifest_changed:
    print("✅ No new characters and no manifest change. Skipping workflow.")
    sys.exit(78)  # special skip code
else:
    sys.exit(0)
