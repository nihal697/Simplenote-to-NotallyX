import json
import os
import re
import zipfile
from datetime import datetime
from html import escape
import shutil

# ===== CONFIGURATION =====
SOURCE_FILE = "simplenote_export.json"
OUTPUT_FOLDER = "google_keep_notes"
ZIP_FILENAME = "google_keep_notes.zip"
LABELS_FILE = "Labels.txt"

# ===== HELPERS =====

def iso_to_usec(iso_str):
    dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
    return int(dt.timestamp() * 1_000_000), dt

def to_html(text):
    lines = text.strip().split('\n')
    html_lines = [
        f'<p dir="ltr" style="line-height:1.38;margin-top:0.0pt;margin-bottom:0.0pt;">'
        f'<span style="font-size:7.2pt;font-family:\'Google Sans\';color:#000000;'
        f'background-color:transparent;font-weight:400;font-style:normal;font-variant:normal;'
        f'text-decoration:none;vertical-align:baseline;white-space:pre;white-space:pre-wrap;">'
        f'{escape(line)}</span></p>' for line in lines
    ]
    return ''.join(html_lines)

def safe_filename(title, fallback_dt, original_title, note_id):
    suffix = "_" + note_id[:6] if note_id else ""
    if title:
        cleaned = re.sub(r'[\r\n\t\\/:"*?<>|]+', '', title).strip()
        truncated = cleaned[:60]
        if len(cleaned) < len(original_title.strip()) or not original_title.strip()[-1].isalnum():
            truncated += "_"
        return f"{truncated}{suffix}.json"
    else:
        return fallback_dt.isoformat().replace(":", "_") + f"{suffix}.json"

# ===== MAIN =====

# Clean output folder before writing
if os.path.exists(OUTPUT_FOLDER):
    shutil.rmtree(OUTPUT_FOLDER)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Load source data
with open(SOURCE_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

# Deduplicate by ID
all_notes = data.get("activeNotes", [])
unique_notes = {}
for note in all_notes:
    note_id = note.get("id")
    if note_id and note_id not in unique_notes:
        unique_notes[note_id] = note
notes = list(unique_notes.values())

all_labels = set()
file_count = 0

for note in notes:
    raw_content = note.get("content", "")

    # Title/body logic
    split_index = raw_content.find("\r\n")
    if split_index == -1:
        title = raw_content.strip()
        body = ""
    else:
        title = raw_content[:split_index].strip()
        body = raw_content[split_index + 2:].strip()

    note_id = note.get("id", "")
    created_usec, created_dt = iso_to_usec(note["creationDate"])
    modified_usec, _ = iso_to_usec(note["lastModified"])
    tags = note.get("tags", [])

    if tags:
        for tag in tags:
            tag_clean = tag.strip()
            if tag_clean:
                all_labels.add(tag_clean)

    note_dict = {
        "color": "DEFAULT",
        "isTrashed": False,
        "isPinned": False,
        "isArchived": False,
        "textContent": body,
        "title": title,
        "userEditedTimestampUsec": modified_usec,
        "createdTimestampUsec": created_usec,
        "textContentHtml": to_html(body),
        "labels": [{"name": tag} for tag in tags] if tags else []
    }

    filename = safe_filename(title, created_dt, title, note_id)
    filepath = os.path.join(OUTPUT_FOLDER, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(note_dict, f, ensure_ascii=False, indent=2)
    file_count += 1

# Write Labels.txt
labels_path = os.path.join(OUTPUT_FOLDER, LABELS_FILE)
with open(labels_path, "w", encoding="utf-8") as f:
    for label in sorted(all_labels, key=str.casefold):
        f.write(f"{label}\n")

# Zip everything
with zipfile.ZipFile(ZIP_FILENAME, "w", zipfile.ZIP_DEFLATED) as zipf:
    for file in os.listdir(OUTPUT_FOLDER):
        zipf.write(os.path.join(OUTPUT_FOLDER, file), arcname=file)

print(f"✅ {file_count} notes + Labels.txt exported and zipped to: {ZIP_FILENAME}")
