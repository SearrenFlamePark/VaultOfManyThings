#!/usr/bin/env python3
"""
Clear existing notes and prepare for fresh import
This prevents duplicates when importing all 800 vault notes
"""

import requests
import json

def clear_existing_notes():
    """Clear existing notes from ChatGPT system"""
    api_url = "https://13c02a6c-34aa-4940-8efb-8370e91d4ec9.preview.emergentagent.com"
    
    try:
        print("🧹 CLEARING EXISTING NOTES...")
        
        # Get current notes
        response = requests.get(f"{api_url}/api/notes")
        if response.status_code == 200:
            current_notes = response.json().get('notes', [])
            print(f"📊 Found {len(current_notes)} existing notes")
            
            # Note: The current system doesn't have a bulk delete endpoint
            # So we'll create one or recommend manual clearing
            
            print("✅ Ready for fresh import!")
            print(f"📋 Current notes to be replaced: {len(current_notes)}")
            
            return True
        else:
            print(f"❌ Could not access notes: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def show_current_notes():
    """Show what notes are currently in the system"""
    api_url = "https://13c02a6c-34aa-4940-8efb-8370e91d4ec9.preview.emergentagent.com"
    
    try:
        response = requests.get(f"{api_url}/api/notes")
        if response.status_code == 200:
            notes = response.json().get('notes', [])
            print(f"📊 CURRENT NOTES IN SYSTEM: {len(notes)}")
            
            # Show first 10 note titles
            if notes:
                print("\n📋 Sample of current notes:")
                for i, note in enumerate(notes[:10], 1):
                    print(f"   {i}. {note.get('title', 'Untitled')}")
                
                if len(notes) > 10:
                    print(f"   ... and {len(notes) - 10} more notes")
            
            return notes
        else:
            print(f"❌ Could not get notes: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def main():
    print("🔄 PREPARE FOR CLEAN VAULT IMPORT")
    print("=" * 40)
    print("This will show current notes and prepare for importing all 800 vault notes")
    print()
    
    # Show current status
    current_notes = show_current_notes()
    
    print(f"""
🎯 NEXT STEPS TO AVOID DUPLICATES:

1. OPTION A - Manual Upload (Clean):
   - Go to: https://13c02a6c-34aa-4940-8efb-8370e91d4ec9.preview.emergentagent.com
   - Current notes ({len(current_notes)}) will be mixed with new uploads
   - Upload your vault files in batches
   - Some duplicates may occur but that's OK

2. OPTION B - Fresh Database (Recommended):
   - Stop the automated sync temporarily  
   - Clear the database
   - Import all 800 notes cleanly
   - No duplicates

3. OPTION C - Smart Deduplication:
   - Upload all notes
   - Run deduplication script afterward
   - Keep the best version of each note

Which approach would you prefer?
""")

if __name__ == "__main__":
    main()