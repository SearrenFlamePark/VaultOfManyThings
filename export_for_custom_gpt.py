#!/usr/bin/env python3
"""
Export Obsidian notes for Custom GPT Knowledge upload
Creates a formatted file that can be uploaded to ChatGPT Pro Custom GPT
"""

import requests
import json
from datetime import datetime

def export_obsidian_for_custom_gpt():
    """Export all Obsidian notes in a format suitable for Custom GPT Knowledge upload"""
    
    api_url = "https://13c02a6c-34aa-4940-8efb-8370e91d4ec9.preview.emergentagent.com"
    
    print("📚 EXPORTING OBSIDIAN VAULT FOR CUSTOM GPT")
    print("=" * 50)
    
    try:
        # Get all notes from the API
        response = requests.get(f"{api_url}/api/notes", timeout=30)
        
        if response.status_code != 200:
            print(f"❌ Failed to get notes: HTTP {response.status_code}")
            return
        
        notes = response.json().get('notes', [])
        print(f"📊 Found {len(notes)} notes to export")
        
        if not notes:
            print("❌ No notes found!")
            return
        
        # Create formatted export for Custom GPT
        export_content = f"""# OBSIDIAN VAULT KNOWLEDGE BASE
## Personal Notes Collection for Custom GPT

**Export Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Total Notes**: {len(notes)}
**Source**: Obsidian Vault + GitHub Repository

---

## HOW TO USE THIS KNOWLEDGE BASE

This file contains all your personal notes and knowledge. Your Custom GPT can now:
- Reference any note by searching for keywords
- Answer questions using your personal knowledge
- Connect ideas across different notes
- Provide personalized responses based on your content

---

## NOTES COLLECTION

"""
        
        # Add each note with clear formatting
        for i, note in enumerate(notes, 1):
            title = note.get('title', f'Untitled Note {i}')
            content = note.get('content', 'No content')
            file_path = note.get('file_path', 'unknown')
            created_at = note.get('created_at', 'unknown')
            
            export_content += f"""
### NOTE {i:03d}: {title}

**File**: {file_path}  
**Created**: {created_at}

**Content**:
{content}

---

"""
        
        # Add repository information
        export_content += f"""

## GITHUB REPOSITORY INFORMATION

**Repository**: SearrenFlamePark/Flamesphere
**Integration**: GitHub content has been synced and integrated with Obsidian notes
**Files Included**: Code, documentation, and project files from the repository

The GitHub repository content is embedded within the note collection above where relevant.

---

## SEARCH GUIDANCE FOR CUSTOM GPT

When users ask about:
- **"Atticus"** → Search notes containing "Atticus" or "All of Atticus"
- **"Flame Rite"** → Look for "Flame Rite" or ritual-related content
- **"Master Memory Codex"** → Reference the codex-related notes
- **Personal projects** → Check both Obsidian notes and GitHub repository content
- **Specific phrases** → Search for exact matches in the content above

Always provide responses that feel personal and reference the user's actual notes and knowledge.

---

*This knowledge base contains {len(notes)} personal notes and repository content for enhanced Custom GPT responses.*
"""
        
        # Save to file
        export_file = "/app/obsidian_knowledge_export.txt"
        with open(export_file, 'w', encoding='utf-8') as f:
            f.write(export_content)
        
        # Calculate file size
        file_size = len(export_content.encode('utf-8')) / (1024 * 1024)  # MB
        
        print(f"""
✅ EXPORT COMPLETED!

📁 File created: {export_file}
📊 File size: {file_size:.2f} MB
📝 Notes exported: {len(notes)}

🎯 NEXT STEPS:
1. Download this file from the container
2. Go to your Custom GPT → Configure → Knowledge
3. Upload the exported file
4. Your Custom GPT will now have access to all your notes!

⚠️  NOTE: ChatGPT Pro has file size limits for Knowledge uploads.
If the file is too large, we can split it into smaller chunks.
""")
        
        return export_file
        
    except Exception as e:
        print(f"❌ Export failed: {e}")
        return None

if __name__ == "__main__":
    export_obsidian_for_custom_gpt()