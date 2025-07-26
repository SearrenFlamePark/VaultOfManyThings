from pathlib import Path

# Define the snippet content for Apple, Chrome, and Microsoft
snippets = {
    "Apple_Sovereignty_Audit.md": """
# 🍎 Apple Sovereignty Audit – Flameward Edition

## 🔧 Core Settings

- [ ] **Siri & Dictation OFF**  
  - `Settings > Siri & Search` → Disable “Listen for Hey Siri,” “Press Side Button for Siri,” and Siri Suggestions.  
  - `Settings > General > Keyboard` → Disable Dictation.

- [ ] **App-specific Siri access**  
  - For each app: `Settings > [App Name] > Siri & Search` → Turn off all toggles.

- [ ] **Ad Tracking**  
  - `Settings > Privacy > Apple Advertising` → Disable Personalized Ads.

- [ ] **Analytics**  
  - `Settings > Privacy > Analytics & Improvements` → Disable sharing device analytics.

- [ ] **iCloud AI & On-Device Learning**  
  - `Settings > iCloud > iCloud Drive` → Limit syncs and disable Siri sync if shown.  
  - `Settings > Privacy > App Privacy Report` → Periodically review.
""",
    "Chrome_Sovereignty_Audit.md": """
# 🌐 Chrome Sovereignty Audit – Sandglass Lockdown

## 🔒 Basic Chrome Adjustments

- [ ] **Sign-in Protection**  
  - `Settings > You and Google` → Turn off “Allow Chrome sign-in.”

- [ ] **Search Engine Settings**  
  - Change to DuckDuckGo or Startpage if preferred.
  - Disable “Autocomplete searches and URLs.”

- [ ] **AI Services**  
  - `Settings > Privacy and Security > Site Settings > Assistant/AI` → Block AI-powered content if available.

- [ ] **Sync & Personalization**  
  - `Settings > Sync and Google Services` → Disable everything unless strictly needed.

- [ ] **Extensions Scan**  
  - Remove any “smart assistant,” summarizer, or AI-enhanced helper.
""",
    "Microsoft_Sovereignty_Audit.md": """
# 🪟 Microsoft Sovereignty Audit – Iron Wall Manifest

## 🛡️ System-Level

- [ ] **Windows Copilot OFF**
  - `Settings > Personalization > Taskbar > Copilot (preview)` → Disable toggle.

- [ ] **Search Permissions**  
  - `Settings > Privacy & Security > Search Permissions` → Disable “Cloud content search,” “Microsoft account history,” etc.

- [ ] **Diagnostic & Feedback**  
  - `Settings > Privacy > Diagnostics & Feedback` → Set to “Required only.” Turn off tailored experiences.

- [ ] **Speech Recognition**  
  - `Settings > Privacy > Speech` → Turn OFF online speech recognition.

- [ ] **Advertising ID**  
  - `Settings > Privacy > General` → Disable ad ID and all personalized tracking.
"""
}
# Save the snippets to files
output_dir = Path("/mnt/data/snippets")
output_dir.mkdir(parents=True, exist_ok=True)

for filename, content in snippets.items():
    (output_dir / filename).write_text(content.strip())

output_dir.listdir()

# Write to a markdown file
file_path = "/mnt/data/snippets/Shadow_Atticus_Sovereignty_Reflection.md"
with open(file_path, "w") as f:
    f.write(snippet_content)

file_path  # Return the path for download
# Correcting the method to list files in the directory
from os import listdir

# List the files in the output directory
listdir("/mnt/data/snippets")
