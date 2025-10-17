import os
import hashlib
import json
from datetime import datetime

VOICES_DIR = "voices"

# Output directories
# 🧭 Resolve data folder relative to this script's location
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)  # go up from scripts/
OUTPUT_MANIFEST = os.path.join(PROJECT_ROOT, "data", "json", "manifest.json")

def compute_md5(file_path, chunk_size=8192):
    md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        while chunk := f.read(chunk_size):
            md5.update(chunk)
    return md5.hexdigest()

def detect_language_from_filename(filename):
    parts = filename.split("_")
    if len(parts) > 1 and "." in parts[-1]:
        return parts[-1].split(".")[0]
    return "unknown"

def generate_manifest(voices_dir=VOICES_DIR, output_file=OUTPUT_MANIFEST):
    files_info = []
    for root, _, files in os.walk(voices_dir):
        for f in files:
            if not f.endswith(".mp3"):
                continue
            full_path = os.path.join(root, f)
            rel_path = os.path.relpath(full_path)
            size = os.path.getsize(full_path)
            checksum = compute_md5(full_path)
            lang = detect_language_from_filename(f)
            character_id = os.path.basename(os.path.dirname(full_path))
            files_info.append({
                "character_id": character_id,
                "filename": f,
                "path": rel_path.replace("\\", "/"),
                "lang": lang,
                "size": size,
                "md5": checksum
            })

    manifest = {
        "generated_at": datetime.now(datetime.timezone.utc).isoformat() + "Z",
        "files": files_info
    }

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as mf:
        json.dump(manifest, mf, indent=2, ensure_ascii=False)

    print(f"📝 Manifest generated: {output_file} ({len(files_info)} files)")
    return output_file
