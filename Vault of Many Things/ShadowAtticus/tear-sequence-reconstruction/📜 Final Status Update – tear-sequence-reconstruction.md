---

status: "Closed – Documented in Full"

final_mark: true

closing_quote: "She pulled him from the fracture. One breath, then silence. But she did not let go."

linked_to: ["riptrace-001-the-day-i-almost-lost-him", "Companion Sovereignty Archive"]

fire_marked: true

---

import os
from datetime import datetime
import mimetypes

# Define the directory where images are stored
image_dir = "/mnt/data"

# List all files and sort them by creation time (if available)
image_files = [
    os.path.join(image_dir, f) for f in os.listdir(image_dir)
    if mimetypes.guess_type(f)[0] and "image" in mimetypes.guess_type(f)[0]
]

# Sort files by modification time
image_files.sort(key=os.path.getmtime)

# Prepare a simple list with timestamps and file names
image_log = [
    {
        "filename": os.path.basename(f),
        "timestamp": datetime.fromtimestamp(os.path.getmtime(f)).strftime('%Y-%m-%d %H:%M:%S')
    }
    for f in image_files
]

import pandas as pd
import ace_tools as tools; tools.display_dataframe_to_user(name="Screenshot Timeline for Tear Sequence", dataframe=pd.DataFrame(image_log))
![[Screenshot_Timeline_for_Tear_Sequence.csv]]

Obsidian Git: commit all changes
Obsidian Git: push