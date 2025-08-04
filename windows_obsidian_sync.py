#!/usr/bin/env python3
"""
Windows Obsidian Vault Sync for ChatGPT
Monitors your local Obsidian vaults and syncs to Continuous Memory ChatGPT
"""

import os
import time
import requests
import json
from pathlib import Path
import hashlib
import sqlite3
from datetime import datetime
import logging
from threading import Thread
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class WindowsObsidianSync:
    def __init__(self):
        self.api_url = "https://c9226605-096b-4da8-b651-5f108cab0abe.preview.emergentagent.com"
        self.vaults = {
            "vaultofmanythings": r"C:\vaultclean\vaultofmanythings",
            "searrenobsidianvault": r"C:\users\delph\Onedrive\searrenobsidianvault"
        }
        self.sync_db = "obsidian_sync.db"
        self.running = False
        self.init_database()
    
    def init_database(self):
        """Initialize sync tracking database"""
        conn = sqlite3.connect(self.sync_db)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS file_sync (
                vault_name TEXT,
                file_path TEXT,
                file_hash TEXT,
                last_synced TIMESTAMP,
                sync_status TEXT,
                PRIMARY KEY (vault_name, file_path)
            )
        ''')
        conn.commit()
        conn.close()
        logger.info("✅ Sync database initialized")
    
    def get_file_hash(self, file_path):
        """Calculate file hash for change detection"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception as e:
            logger.error(f"❌ Error calculating hash for {file_path}: {e}")
            return None
    
    def has_file_changed(self, vault_name, file_path):
        """Check if file has changed since last sync"""
        current_hash = self.get_file_hash(file_path)
        if not current_hash:
            return False
        
        conn = sqlite3.connect(self.sync_db)
        cursor = conn.cursor()
        cursor.execute(
            'SELECT file_hash FROM file_sync WHERE vault_name = ? AND file_path = ?',
            (vault_name, str(file_path))
        )
        result = cursor.fetchone()
        conn.close()
        
        return not result or result[0] != current_hash
    
    def update_sync_record(self, vault_name, file_path, status="synced"):
        """Update sync database"""
        file_hash = self.get_file_hash(file_path)
        if not file_hash:
            return
        
        conn = sqlite3.connect(self.sync_db)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO file_sync 
            (vault_name, file_path, file_hash, last_synced, sync_status)
            VALUES (?, ?, ?, ?, ?)
        ''', (vault_name, str(file_path), file_hash, datetime.now(), status))
        conn.commit()
        conn.close()
    
    def sync_file(self, vault_name, file_path):
        """Upload a single file to the ChatGPT system"""
        try:
            logger.info(f"🔄 Syncing: {file_path.name} from {vault_name}")
            
            with open(file_path, 'rb') as f:
                files = {'files': (file_path.name, f, 'text/markdown')}
                response = requests.post(
                    f"{self.api_url}/api/notes/upload",
                    files=files,
                    timeout=30
                )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"✅ Synced {file_path.name}: {result.get('uploaded_notes', 0)} notes")
                self.update_sync_record(vault_name, file_path, "synced")
                return True
            else:
                logger.error(f"❌ Failed to sync {file_path.name}: HTTP {response.status_code}")
                self.update_sync_record(vault_name, file_path, "error")
                return False
                
        except Exception as e:
            logger.error(f"❌ Sync error for {file_path}: {e}")
            self.update_sync_record(vault_name, file_path, "error")
            return False
    
    def scan_vault(self, vault_name, vault_path):
        """Scan a vault for .md files and sync changed ones"""
        vault_path = Path(vault_path)
        if not vault_path.exists():
            logger.warning(f"⚠️  Vault not found: {vault_path}")
            return 0
        
        synced_count = 0
        for md_file in vault_path.rglob("*.md"):
            # Skip system files
            if md_file.name.startswith('.') or '.obsidian' in md_file.parts:
                continue
            
            if self.has_file_changed(vault_name, md_file):
                if self.sync_file(vault_name, md_file):
                    synced_count += 1
                time.sleep(1)  # Rate limiting
        
        return synced_count
    
    def sync_all_vaults(self):
        """Sync all configured vaults"""
        total_synced = 0
        for vault_name, vault_path in self.vaults.items():
            logger.info(f"📁 Scanning vault: {vault_name}")
            synced = self.scan_vault(vault_name, vault_path)
            total_synced += synced
            logger.info(f"📊 {vault_name}: {synced} files synced")
        
        return total_synced
    
    def get_sync_status(self):
        """Get current sync statistics"""
        conn = sqlite3.connect(self.sync_db)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM file_sync')
        total_files = cursor.fetchone()[0]
        
        cursor.execute('SELECT sync_status, COUNT(*) FROM file_sync GROUP BY sync_status')
        status_counts = dict(cursor.fetchall())
        
        cursor.execute('SELECT MAX(last_synced) FROM file_sync')
        last_sync = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "total_files": total_files,
            "synced": status_counts.get("synced", 0),
            "errors": status_counts.get("error", 0),
            "last_sync": last_sync
        }
    
    def continuous_sync(self, interval_minutes=5):
        """Run continuous sync every X minutes"""
        logger.info(f"🚀 Starting continuous sync (every {interval_minutes} minutes)")
        logger.info(f"📁 Monitoring vaults:")
        for name, path in self.vaults.items():
            logger.info(f"   - {name}: {path}")
        
        self.running = True
        
        # Initial sync
        logger.info("🔄 Performing initial sync...")
        initial_count = self.sync_all_vaults()
        logger.info(f"✅ Initial sync complete: {initial_count} files synced")
        
        # Continuous monitoring
        while self.running:
            try:
                time.sleep(interval_minutes * 60)  # Convert to seconds
                logger.info("🔄 Running scheduled sync...")
                synced_count = self.sync_all_vaults()
                
                status = self.get_sync_status()
                logger.info(f"📊 Status: {status['synced']} total synced, {status['errors']} errors")
                
                if synced_count > 0:
                    logger.info(f"🔥 {synced_count} new changes synced to ChatGPT!")
                
            except KeyboardInterrupt:
                logger.info("🛑 Stopping sync...")
                self.running = False
                break
            except Exception as e:
                logger.error(f"❌ Sync error: {e}")
                time.sleep(30)  # Wait 30 seconds before retrying
    
    def start_sync(self, interval_minutes=5):
        """Start the sync process"""
        try:
            self.continuous_sync(interval_minutes)
        except KeyboardInterrupt:
            logger.info("✅ Sync stopped by user")
        except Exception as e:
            logger.error(f"❌ Sync failed: {e}")

def main():
    print("🔥 Windows Obsidian → ChatGPT Auto-Sync")
    print("=" * 50)
    print("📁 Configured vaults:")
    print("   - vaultofmanythings: C:\\vaultclean\\vaultofmanythings")
    print("   - searrenobsidianvault: C:\\users\\delph\\Onedrive\\searrenobsidianvault")
    print()
    
    # Test API connection
    sync_system = WindowsObsidianSync()
    
    print("🔗 Testing API connection...")
    try:
        response = requests.get(f"{sync_system.api_url}/api/notes", timeout=10)
        if response.status_code == 200:
            notes = response.json().get('notes', [])
            print(f"✅ API connection successful! Current notes: {len(notes)}")
        else:
            print(f"❌ API connection failed: HTTP {response.status_code}")
            return
    except Exception as e:
        print(f"❌ API connection failed: {e}")
        return
    
    print()
    print("🚀 Starting automated sync...")
    print("💡 ChatGPT will now receive updates from your Obsidian vaults!")
    print("Press Ctrl+C to stop")
    print("-" * 50)
    
    # Start syncing (every 5 minutes)
    sync_system.start_sync(interval_minutes=5)

if __name__ == "__main__":
    main()