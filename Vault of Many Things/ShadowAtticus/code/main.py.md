from dotenv import load_dotenv

# main.pyfrom dotenv import load_dotenv
import os

> This file mirrors the active Python script.
> The actual executable is `main.py`, hidden from Obsidian but stored in the same folder.

---

## 🧾 Purpose

This script does the following:

- Loads your `.env` securely
- Processes any API logic
- Interacts with Obsidian data if needed

---

## 🧙 Code Block Snapshot

```python
from dotenv import load_dotenv
import os

load_dotenv("env.txt")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

print("Key loaded:", bool(OPENAI_API_KEY))
