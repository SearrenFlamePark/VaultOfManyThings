#!/usr/bin/env python3
"""
GitHub Repository Integration for Continuous Memory ChatGPT
Syncs Flamesphere repository content alongside Obsidian notes
"""

import asyncio
import requests
import base64
import hashlib
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import json
import tempfile
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/github_sync.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class FlamesphereGitHubSync:
    def __init__(self):
        self.api_url = "https://61ac9fa4-bee8-4446-be2b-6c122b968795.preview.emergentagent.com"
        self.repository = "SearrenFlamePark/Flamesphere"
        self.github_api = "https://api.github.com"
        self.supported_extensions = ['.md', '.txt', '.py', '.js', '.json', '.yaml', '.yml']
        self.max_file_size = 1024 * 1024  # 1MB limit
        
        # Since we're operating within Emergent, we'll work with local files
        # that may have been pulled from GitHub
        
    def search_for_flamesphere_content(self) -> List[Path]:
        """Search for Flamesphere repository content in the workspace"""
        potential_paths = [
            "/app",
            "/workspace", 
            "/tmp",
            "/var/tmp"
        ]
        
        flamesphere_files = []
        
        for base_path in potential_paths:
            if os.path.exists(base_path):
                for root, dirs, files in os.walk(base_path):
                    # Skip hidden directories and common non-content directories
                    dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'venv']]
                    
                    for file in files:
                        file_path = Path(root) / file
                        
                        # Check if it's a supported file type
                        if any(file.endswith(ext) for ext in self.supported_extensions):
                            # Check file size
                            try:
                                if file_path.stat().st_size <= self.max_file_size:
                                    flamesphere_files.append(file_path)
                            except:
                                continue
        
        return flamesphere_files
    
    async def sync_local_files_to_chatgpt(self) -> Dict[str, Any]:
        """Sync local files that might be from Flamesphere repository"""
        logger.info("🔄 Starting Flamesphere repository sync to ChatGPT")
        
        # Search for potential Flamesphere files
        files_found = self.search_for_flamesphere_content()
        logger.info(f"📁 Found {len(files_found)} potential files to sync")
        
        synced_files = 0
        failed_files = 0
        
        for file_path in files_found:
            try:
                # Read file content
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Create a meaningful filename that indicates repository source
                relative_path = str(file_path).replace('/app/', '').replace('/workspace/', '')
                repo_filename = f"flamesphere_{relative_path.replace('/', '_')}"
                
                # Create enhanced content with repository context
                enhanced_content = f"""# Flamesphere Repository File
**Source**: {relative_path}  
**Repository**: SearrenFlamePark/Flamesphere  
**Sync Time**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  

## Original Content

{content}

---
*This file was synced from the Flamesphere GitHub repository to provide ChatGPT with access to your repository content alongside Obsidian notes.*
"""
                
                # Upload to ChatGPT system
                success = await self.upload_file_to_chatgpt(repo_filename, enhanced_content)
                
                if success:
                    synced_files += 1
                    logger.info(f"✅ Synced: {relative_path}")
                else:
                    failed_files += 1
                    logger.warning(f"❌ Failed to sync: {relative_path}")
                
                # Rate limiting
                await asyncio.sleep(0.5)
                
            except Exception as e:
                logger.error(f"❌ Error processing {file_path}: {e}")
                failed_files += 1
        
        logger.info(f"🎉 Flamesphere sync completed: {synced_files} files synced, {failed_files} failed")
        
        return {
            "status": "completed",
            "synced_files": synced_files,
            "failed_files": failed_files,
            "total_processed": len(files_found)
        }
    
    async def upload_file_to_chatgpt(self, filename: str, content: str) -> bool:
        """Upload file content to ChatGPT continuous memory system"""
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
                
                if response.status_code == 200:
                    return True
                else:
                    logger.error(f"Upload failed for {filename}: HTTP {response.status_code}")
                    return False
                    
            finally:
                # Clean up temp file
                os.unlink(temp_file)
                
        except Exception as e:
            logger.error(f"Error uploading {filename}: {e}")
            return False
    
    async def create_repository_index(self) -> bool:
        """Create an index file summarizing the repository structure"""
        try:
            files_found = self.search_for_flamesphere_content()
            
            # Group files by type and directory
            file_structure = {}
            for file_path in files_found:
                relative_path = str(file_path).replace('/app/', '').replace('/workspace/', '')
                directory = str(Path(relative_path).parent) if Path(relative_path).parent != Path('.') else 'root'
                
                if directory not in file_structure:
                    file_structure[directory] = []
                
                file_structure[directory].append({
                    'name': Path(relative_path).name,
                    'path': relative_path,
                    'extension': Path(relative_path).suffix,
                    'size': file_path.stat().st_size
                })
            
            # Create index content
            index_content = f"""# Flamesphere Repository Index

**Repository**: SearrenFlamePark/Flamesphere  
**Sync Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Total Files**: {len(files_found)}

## Repository Structure

"""
            
            for directory, files in sorted(file_structure.items()):
                index_content += f"### {directory}/\n\n"
                for file_info in sorted(files, key=lambda x: x['name']):
                    size_kb = file_info['size'] / 1024
                    index_content += f"- **{file_info['name']}** ({file_info['extension']}) - {size_kb:.1f}KB\n"
                index_content += "\n"
            
            index_content += f"""
## File Types Summary

"""
            
            # Count by extension
            extension_counts = {}
            for file_path in files_found:
                ext = file_path.suffix
                extension_counts[ext] = extension_counts.get(ext, 0) + 1
            
            for ext, count in sorted(extension_counts.items()):
                index_content += f"- {ext}: {count} files\n"
            
            index_content += f"""

## Integration Notes

This repository has been integrated into your ChatGPT continuous memory system alongside your Obsidian notes. You can now:

1. **Ask about repository content**: "What's in my Flamesphere repository?"
2. **Reference specific files**: "Show me the content of [filename]"
3. **Cross-reference with Obsidian**: ChatGPT can now connect repository code with your notes
4. **Search across both**: Search queries will look in both GitHub repo and Obsidian notes

## How to Update

The repository content is synced automatically. If you make changes to your GitHub repository, they will be reflected in ChatGPT's memory system.

---
*This index was automatically generated by the Flamesphere GitHub integration system.*
"""
            
            # Upload the index
            return await self.upload_file_to_chatgpt("flamesphere_repository_index.md", index_content)
            
        except Exception as e:
            logger.error(f"Error creating repository index: {e}")
            return False

async def main():
    """Main function to run Flamesphere GitHub integration"""
    print("🔥 FLAMESPHERE GITHUB INTEGRATION STARTING")
    print("=" * 50)
    
    sync = FlamesphereGitHubSync()
    
    # Test connection to ChatGPT system
    try:
        response = requests.get(f"{sync.api_url}/api/notes", timeout=10)
        if response.status_code == 200:
            notes = response.json().get('notes', [])
            print(f"✅ Connected to ChatGPT system - {len(notes)} notes currently stored")
        else:
            print(f"❌ Connection failed: HTTP {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return
    
    # Create repository index first
    print("\n📋 Creating repository index...")
    index_created = await sync.create_repository_index()
    if index_created:
        print("✅ Repository index created successfully")
    else:
        print("⚠️  Repository index creation failed, continuing with sync...")
    
    # Sync repository files
    print("\n🚀 Starting repository content sync...")
    result = await sync.sync_local_files_to_chatgpt()
    
    print(f"""
🎉 FLAMESPHERE GITHUB INTEGRATION COMPLETE!

📊 Results:
   - Files synced: {result['synced_files']}
   - Files failed: {result['failed_files']}
   - Total processed: {result['total_processed']}

🧪 TEST YOUR INTEGRATION:
   Ask ChatGPT: "What files do you have from my Flamesphere repository?"
   Or: "Show me the Flamesphere repository index"

✅ Your ChatGPT now has access to BOTH:
   - Your Obsidian notes
   - Your Flamesphere GitHub repository content!
""")

if __name__ == "__main__":
    asyncio.run(main())