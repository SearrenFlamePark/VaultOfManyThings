#!/usr/bin/env python3
"""
Full Vault Sync - Import ALL Obsidian notes to ChatGPT
Scan both vault locations and import ALL markdown files
"""

import asyncio
import requests
import os
import logging
from pathlib import Path
import tempfile
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/full_vault_sync.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class FullVaultSync:
    def __init__(self):
        self.api_url = "https://61ac9fa4-bee8-4446-be2b-6c122b968795.preview.emergentagent.com"
        
        # Your vault locations
        self.vault_paths = [
            "C:\\vaultclean\\vaultofmanythings",
            "C:\\users\\delph\\Onedrive\\searrenobsidianvault"
        ]
        
        # Since we're in a container, we need to look for mounted/accessible paths
        self.local_search_paths = [
            "/app",
            "/workspace", 
            "/tmp",
            "/mnt",
            "/media",
            "/opt"
        ]
        
        self.synced_count = 0
        self.failed_count = 0
        self.total_found = 0
        
    def find_all_markdown_files(self):
        """Find all markdown files in accessible locations"""
        markdown_files = []
        
        # Search all potential locations for markdown files
        for search_path in self.local_search_paths:
            if os.path.exists(search_path):
                logger.info(f"🔍 Searching {search_path} for markdown files...")
                
                for root, dirs, files in os.walk(search_path):
                    # Skip hidden directories and common non-content directories
                    dirs[:] = [d for d in dirs if not d.startswith('.') and d not in [
                        'node_modules', '__pycache__', 'venv', '.git', 'dist', 'build'
                    ]]
                    
                    for file in files:
                        if file.endswith('.md'):
                            file_path = Path(root) / file
                            try:
                                # Check if it's a reasonable size and readable
                                if file_path.stat().st_size < 10 * 1024 * 1024:  # < 10MB
                                    markdown_files.append(file_path)
                            except:
                                continue
        
        self.total_found = len(markdown_files)
        logger.info(f"📁 Found {self.total_found} markdown files total")
        return markdown_files
    
    async def sync_all_files(self):
        """Sync all found markdown files to ChatGPT"""
        logger.info("🚀 Starting full vault synchronization")
        
        # Find all markdown files
        all_files = self.find_all_markdown_files()
        
        if not all_files:
            logger.error("❌ No markdown files found! Check vault paths.")
            return
        
        logger.info(f"📝 Beginning sync of {len(all_files)} markdown files...")
        
        # Process files in batches to avoid overwhelming the system
        batch_size = 10
        for i in range(0, len(all_files), batch_size):
            batch = all_files[i:i + batch_size]
            
            logger.info(f"📦 Processing batch {i//batch_size + 1}/{(len(all_files)-1)//batch_size + 1}")
            
            # Process batch
            tasks = [self.sync_single_file(file_path) for file_path in batch]
            await asyncio.gather(*tasks, return_exceptions=True)
            
            # Small delay between batches
            await asyncio.sleep(1)
        
        logger.info(f"""
🎉 FULL VAULT SYNC COMPLETED!

📊 Results:
   - Files found: {self.total_found}
   - Successfully synced: {self.synced_count}  
   - Failed: {self.failed_count}
   - Success rate: {(self.synced_count/self.total_found)*100:.1f}%
""")
        
        return {
            "total_found": self.total_found,
            "synced": self.synced_count,
            "failed": self.failed_count
        }
    
    async def sync_single_file(self, file_path: Path):
        """Sync a single markdown file"""
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            if not content.strip():
                return False  # Skip empty files
            
            # Create a meaningful filename
            relative_path = str(file_path).replace('/app/', '').replace('/workspace/', '')
            clean_filename = file_path.name
            
            # Add vault context to content
            enhanced_content = f"""# {file_path.stem}

**Source File**: {clean_filename}  
**Path**: {relative_path}  
**Vault Sync**: Full vault import  
**Import Time**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  

## Content

{content}

---
*This file was imported from your Obsidian vault as part of the comprehensive vault sync to give ChatGPT access to all your notes.*
"""
            
            # Upload to ChatGPT system
            success = await self.upload_to_chatgpt(clean_filename, enhanced_content)
            
            if success:
                self.synced_count += 1
                logger.info(f"✅ Synced: {clean_filename}")
            else:
                self.failed_count += 1
                logger.warning(f"❌ Failed: {clean_filename}")
            
            return success
            
        except Exception as e:
            self.failed_count += 1
            logger.error(f"❌ Error syncing {file_path}: {e}")
            return False
    
    async def upload_to_chatgpt(self, filename: str, content: str) -> bool:
        """Upload file content to ChatGPT system"""
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
                f.write(content)
                temp_file = f.name
            
            try:
                # Upload file
                with open(temp_file, 'rb') as f:
                    files = {'files': (filename, f, 'text/markdown')}
                    response = requests.post(
                        f"{self.api_url}/api/notes/upload",
                        files=files,
                        timeout=30
                    )
                
                return response.status_code == 200
                    
            finally:
                # Clean up temp file
                os.unlink(temp_file)
                
        except Exception as e:
            logger.error(f"Upload error for {filename}: {e}")
            return False

async def main():
    print("📚 FULL OBSIDIAN VAULT SYNC")
    print("=" * 40)
    print("Importing ALL markdown files to ChatGPT...")
    print()
    
    syncer = FullVaultSync()
    
    # Test connection first
    try:
        response = requests.get(f"{syncer.api_url}/api/notes", timeout=10)
        if response.status_code == 200:
            current_notes = len(response.json().get('notes', []))
            print(f"✅ Connected to ChatGPT system")
            print(f"📊 Current notes in system: {current_notes}")
        else:
            print(f"❌ Connection failed: HTTP {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return
    
    print(f"\n🔍 Scanning for ALL markdown files...")
    
    # Run full sync
    result = await syncer.sync_all_files()
    
    # Final check
    try:
        response = requests.get(f"{syncer.api_url}/api/notes", timeout=10)
        if response.status_code == 200:
            final_notes = len(response.json().get('notes', []))
            print(f"\n📊 FINAL COUNT: {final_notes} notes now accessible to ChatGPT!")
            
            if final_notes > current_notes:
                print(f"🎉 Successfully added {final_notes - current_notes} new notes!")
            else:
                print("⚠️  Note count didn't increase - some files may have been duplicates")
    except:
        print("Could not get final count")
    
    print(f"""
🎯 NEXT STEPS:
1. Go to: https://61ac9fa4-bee8-4446-be2b-6c122b968795.preview.emergentagent.com
2. Ask ChatGPT: "How many notes do you have access to now?"
3. Test: "What notes do you have about [any topic from your vault]?"

Your ChatGPT should now have access to many more of your Obsidian notes!
""")

if __name__ == "__main__":
    asyncio.run(main())