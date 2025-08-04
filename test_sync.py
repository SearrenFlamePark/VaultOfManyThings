#!/usr/bin/env python3
"""
Quick test to verify sync system functionality
"""

import requests
import tempfile
import time
from pathlib import Path

def test_api_connection():
    """Test connection to continuous memory API"""
    print("🔗 Testing API connection...")
    
    api_url = "https://c9226605-096b-4da8-b651-5f108cab0abe.preview.emergentagent.com"
    
    try:
        response = requests.get(f"{api_url}/api/notes", timeout=10)
        if response.status_code == 200:
            data = response.json()
            note_count = len(data.get('notes', []))
            print(f"✅ API connection successful!")
            print(f"📊 Current notes in system: {note_count}")
            return True
        else:
            print(f"❌ API returned status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ API connection failed: {e}")
        return False

def test_file_upload():
    """Test uploading a file to verify the system works"""
    print("\n📤 Testing file upload...")
    
    api_url = "https://c9226605-096b-4da8-b651-5f108cab0abe.preview.emergentagent.com"
    
    # Create a test file
    test_content = f"""# Sync Test {time.time()}

This is a test note created by the Obsidian Auto-Sync system.

## Test Details
- Created: {time.strftime('%Y-%m-%d %H:%M:%S')}
- Purpose: Verify sync functionality
- Status: Testing automated upload

## System Integration
This test confirms that your Vault of Many Things can successfully sync with the Continuous Memory ChatGPT system.

**Test successful if you can see this note in your ChatGPT system!** 🔥
"""
    
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(test_content)
            temp_file = Path(f.name)
        
        # Upload the file
        with open(temp_file, 'rb') as f:
            files = {'files': ('sync_test.md', f, 'text/markdown')}
            response = requests.post(f"{api_url}/api/notes/upload", files=files, timeout=30)
        
        # Clean up
        temp_file.unlink()
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ File upload successful!")
            print(f"📊 Uploaded: {result.get('uploaded_notes', 0)} notes")
            return True
        else:
            print(f"❌ Upload failed with status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Upload test failed: {e}")
        return False

def main():
    print("🧪 Testing Obsidian Auto-Sync System")
    print("=" * 40)
    
    # Test API connection
    api_ok = test_api_connection()
    
    if api_ok:
        # Test file upload
        upload_ok = test_file_upload()
        
        if upload_ok:
            print(f"\n🎉 All tests passed!")
            print(f"Your Obsidian Auto-Sync system is ready to use!")
            print(f"\nNext steps:")
            print(f"1. Run: python /app/setup_obsidian_sync.py")
            print(f"2. Point it to your Obsidian vault")
            print(f"3. Start syncing automatically!")
        else:
            print(f"\n⚠️  API connection works, but upload failed")
            print(f"Check the system logs for details")
    else:
        print(f"\n❌ API connection failed")
        print(f"Make sure your continuous memory system is running")

if __name__ == "__main__":
    main()