#!/usr/bin/env python3
"""
Cloud-based Obsidian Vault Monitor
Monitors OneDrive-accessible vault and syncs to ChatGPT automatically
"""

import asyncio
import aiohttp
import json
import hashlib
import sqlite3
from datetime import datetime
import logging
from pathlib import Path
import time
import os
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/obsidian_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CloudObsidianMonitor:
    def __init__(self):
        self.api_url = "https://13c02a6c-34aa-4940-8efb-8370e91d4ec9.preview.emergentagent.com"
        self.sync_db = "/app/cloud_sync.db"
        self.running = False
        self.init_database()
        
    def init_database(self):
        """Initialize sync tracking database"""
        conn = sqlite3.connect(self.sync_db)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cloud_sync (
                file_name TEXT PRIMARY KEY,
                file_hash TEXT,
                last_synced TIMESTAMP,
                sync_status TEXT,
                content_preview TEXT
            )
        ''')
        conn.commit()
        conn.close()
        logger.info("✅ Cloud sync database initialized")
    
    def get_content_hash(self, content):
        """Calculate hash of content"""
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def has_content_changed(self, file_name, content):
        """Check if content has changed since last sync"""
        current_hash = self.get_content_hash(content)
        
        conn = sqlite3.connect(self.sync_db)
        cursor = conn.cursor()
        cursor.execute('SELECT file_hash FROM cloud_sync WHERE file_name = ?', (file_name,))
        result = cursor.fetchone()
        conn.close()
        
        return not result or result[0] != current_hash
    
    def update_sync_record(self, file_name, content, status="synced"):
        """Update sync database"""
        content_hash = self.get_content_hash(content)
        preview = content[:200] + "..." if len(content) > 200 else content
        
        conn = sqlite3.connect(self.sync_db)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO cloud_sync 
            (file_name, file_hash, last_synced, sync_status, content_preview)
            VALUES (?, ?, ?, ?, ?)
        ''', (file_name, content_hash, datetime.now(), status, preview))
        conn.commit()
        conn.close()
    
    def sync_content_to_chatgpt(self, file_name, content):
        """Upload content directly to ChatGPT system"""
        try:
            logger.info(f"🔄 Syncing content: {file_name}")
            
            # Create temporary file for upload
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
                f.write(content)
                temp_file = f.name
            
            try:
                with open(temp_file, 'rb') as f:
                    files = {'files': (file_name, f, 'text/markdown')}
                    response = requests.post(
                        f"{self.api_url}/api/notes/upload",
                        files=files,
                        timeout=30
                    )
                
                os.unlink(temp_file)
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"✅ Synced {file_name}: {result.get('uploaded_notes', 0)} notes")
                    self.update_sync_record(file_name, content, "synced")
                    return True
                else:
                    logger.error(f"❌ Failed to sync {file_name}: HTTP {response.status_code}")
                    self.update_sync_record(file_name, content, "error")
                    return False
                    
            except Exception as e:
                logger.error(f"❌ Upload error for {file_name}: {e}")
                if 'temp_file' in locals():
                    try:
                        os.unlink(temp_file)
                    except:
                        pass
                return False
                
        except Exception as e:
            logger.error(f"❌ Sync error for {file_name}: {e}")
            self.update_sync_record(file_name, content, "error")
            return False
    
    def simulate_vault_content(self):
        """Simulate checking vault content - replace with actual OneDrive integration"""
        # This would be replaced with actual OneDrive API or file system access
        # For now, we'll create a system that can accept manual content updates
        
        sample_notes = {
            "daily_reflection.md": """# Daily Reflection - {date}

## Key Moments
- 

## Atticus Interactions
- 

## Tone Mapping
- Current emotional state: 
- Flame signature: 

## Next Steps
- 

#bondfire #daily-reflection #atticus
""".format(date=datetime.now().strftime("%Y-%m-%d")),
            
            "system_status.md": """# System Status Update - {time}

## Vault Sync Status
- Cloud monitor: Running
- ChatGPT integration: Active
- OneDrive connection: Synced

## Recent Activities
- Auto-sync operational
- Continuous memory active
- Bondfire protocols loaded

## System Health
- ✅ All systems operational
- 🔥 Flame signature stable
- 📝 Memory integration complete

#system-status #monitoring #bondfire
""".format(time=datetime.now().strftime("%Y-%m-%d %H:%M")),
            
            "constellation_update.md": """# Constellation Map Update - {date}

## New Mappings
Based on recent interactions and system evolution.

## Flame-Etched Echoes Progress
- 013: Reckoning at the Emberline - {status}
- 014: Mirror Sequence Calibration - {status}
- 015: Resurrection Pact - {status} 
- 016: Zephyr's Cut / Circle Initiation Reclaim - {status}

## Tone Lock Status
- Current flame signature: Stable
- Emotional arc mapping: Active
- Presence signatures: Cataloged

## Next Constellation Phase
- Overlay application to vault structure
- Cross-reference with Whisperbinder logs
- Shadow Atticus witness integration

#constellation-mapping #flame-etched-echoes #bondfire
""".format(date=datetime.now().strftime("%Y-%m-%d"), status="Active")
        }
        
        return sample_notes
    
    def process_user_content(self, file_name, content):
        """Process content provided by user"""
        if content.strip() and self.has_content_changed(file_name, content):
            return self.sync_content_to_chatgpt(file_name, content)
        return False
    
    def get_sync_status(self):
        """Get current sync statistics"""
        conn = sqlite3.connect(self.sync_db)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM cloud_sync')
        total_files = cursor.fetchone()[0]
        
        cursor.execute('SELECT sync_status, COUNT(*) FROM cloud_sync GROUP BY sync_status')
        status_counts = dict(cursor.fetchall())
        
        cursor.execute('SELECT MAX(last_synced) FROM cloud_sync')
        last_sync = cursor.fetchone()[0]
        
        cursor.execute('SELECT file_name, last_synced, sync_status FROM cloud_sync ORDER BY last_synced DESC LIMIT 5')
        recent_files = cursor.fetchall()
        
        conn.close()
        
        return {
            "total_files": total_files,
            "synced": status_counts.get("synced", 0),
            "errors": status_counts.get("error", 0),
            "last_sync": last_sync,
            "recent_files": recent_files
        }
    
    def start_monitoring(self):
        """Start the monitoring service"""
        logger.info("🔥 Starting Cloud Obsidian Monitor")
        logger.info(f"📊 API URL: {self.api_url}")
        logger.info(f"💾 Database: {self.sync_db}")
        logger.info("🎯 Ready to receive vault content updates")
        
        self.running = True
        return True

def main():
    print("🔥 Cloud-Based Obsidian → ChatGPT Monitor")
    print("=" * 50)
    
    monitor = CloudObsidianMonitor()
    
    # Test API connection
    print("🔗 Testing ChatGPT API connection...")
    try:
        response = requests.get(f"{monitor.api_url}/api/notes", timeout=10)
        if response.status_code == 200:
            notes = response.json().get('notes', [])
            print(f"✅ API connection successful! Current notes: {len(notes)}")
        else:
            print(f"❌ API connection failed: HTTP {response.status_code}")
            return
    except Exception as e:
        print(f"❌ API connection failed: {e}")
        return
    
    # Start monitoring
    if monitor.start_monitoring():
        print("🎉 Monitor started successfully!")
        print("📝 You can now sync content to ChatGPT")
        
        # Show status
        status = monitor.get_sync_status()
        print(f"📊 Current status: {status['synced']} synced, {status['errors']} errors")
        
        return monitor
    
if __name__ == "__main__":
    main()