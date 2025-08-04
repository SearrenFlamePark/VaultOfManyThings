#!/usr/bin/env python3
"""
Obsidian Vault Auto-Sync System
Automatically syncs .md files from Obsidian vault to Continuous Memory ChatGPT
Based on OneDrive Tether Blueprint architecture
"""

import os
import time
import requests
import json
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import hashlib
import sqlite3
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('obsidian_sync.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ObsidianSyncHandler(FileSystemEventHandler):
    """Handles file system events for Obsidian vault changes"""
    
    def __init__(self, api_url, vault_path):
        self.api_url = api_url
        self.vault_path = Path(vault_path)
        self.sync_db_path = self.vault_path / ".obsidian_sync.db"
        self.init_sync_database()
        
    def init_sync_database(self):
        """Initialize SQLite database to track file hashes and sync status"""
        conn = sqlite3.connect(self.sync_db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS file_sync (
                file_path TEXT PRIMARY KEY,
                file_hash TEXT,
                last_synced TIMESTAMP,
                sync_status TEXT
            )
        ''')
        conn.commit()
        conn.close()
        logger.info("Sync database initialized")
    
    def get_file_hash(self, file_path):
        """Calculate MD5 hash of file content"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception as e:
            logger.error(f"Error calculating hash for {file_path}: {e}")
            return None
    
    def is_file_changed(self, file_path):
        """Check if file has changed since last sync"""
        current_hash = self.get_file_hash(file_path)
        if not current_hash:
            return False
            
        conn = sqlite3.connect(self.sync_db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT file_hash FROM file_sync WHERE file_path = ?', (str(file_path),))
        result = cursor.fetchone()
        conn.close()
        
        if not result or result[0] != current_hash:
            return True
        return False
    
    def update_sync_record(self, file_path, status="synced"):
        """Update sync database with latest file info"""
        file_hash = self.get_file_hash(file_path)
        if not file_hash:
            return
            
        conn = sqlite3.connect(self.sync_db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO file_sync 
            (file_path, file_hash, last_synced, sync_status)
            VALUES (?, ?, ?, ?)
        ''', (str(file_path), file_hash, datetime.now(), status))
        conn.commit()
        conn.close()
    
    def sync_file_to_api(self, file_path):
        """Upload file to continuous memory API"""
        try:
            if not file_path.suffix.lower() == '.md':
                return False
                
            logger.info(f"Syncing file: {file_path}")
            
            with open(file_path, 'rb') as f:
                files = {'files': (file_path.name, f, 'text/markdown')}
                response = requests.post(
                    f"{self.api_url}/api/notes/upload",
                    files=files,
                    timeout=30
                )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Successfully synced {file_path.name}: {result.get('uploaded_notes', 0)} notes uploaded")
                self.update_sync_record(file_path, "synced")
                return True
            else:
                logger.error(f"Failed to sync {file_path.name}: HTTP {response.status_code}")
                self.update_sync_record(file_path, "error")
                return False
                
        except Exception as e:
            logger.error(f"Error syncing {file_path}: {e}")
            self.update_sync_record(file_path, "error")
            return False
    
    def on_modified(self, event):
        """Handle file modification events"""
        if not event.is_directory:
            file_path = Path(event.src_path)
            if self.should_sync_file(file_path) and self.is_file_changed(file_path):
                logger.info(f"File modified: {file_path}")
                time.sleep(1)  # Brief delay to ensure file write is complete
                self.sync_file_to_api(file_path)
    
    def on_created(self, event):
        """Handle file creation events"""
        if not event.is_directory:
            file_path = Path(event.src_path)
            if self.should_sync_file(file_path):
                logger.info(f"New file created: {file_path}")
                time.sleep(1)  # Brief delay to ensure file write is complete
                self.sync_file_to_api(file_path)
    
    def should_sync_file(self, file_path):
        """Determine if file should be synced"""
        # Only sync .md files
        if file_path.suffix.lower() != '.md':
            return False
            
        # Skip hidden files and Obsidian system files
        if file_path.name.startswith('.'):
            return False
            
        # Skip files in .obsidian folder
        if '.obsidian' in file_path.parts:
            return False
            
        return True
    
    def initial_sync(self):
        """Perform initial sync of all .md files in vault"""
        logger.info("Starting initial vault sync...")
        synced_count = 0
        
        for md_file in self.vault_path.rglob("*.md"):
            if self.should_sync_file(md_file) and self.is_file_changed(md_file):
                if self.sync_file_to_api(md_file):
                    synced_count += 1
                time.sleep(0.5)  # Rate limiting
        
        logger.info(f"Initial sync completed: {synced_count} files synced")

class ObsidianAutoSync:
    """Main sync coordinator using OneDrive Tether Blueprint architecture"""
    
    def __init__(self, vault_path, api_url):
        self.vault_path = Path(vault_path)
        self.api_url = api_url
        self.observer = None
        self.handler = None
        
        # Validate paths
        if not self.vault_path.exists():
            raise FileNotFoundError(f"Obsidian vault not found: {vault_path}")
        
        logger.info(f"Initialized ObsidianAutoSync for vault: {self.vault_path}")
    
    def start_monitoring(self, perform_initial_sync=True):
        """Start file system monitoring"""
        try:
            self.handler = ObsidianSyncHandler(self.api_url, self.vault_path)
            
            if perform_initial_sync:
                self.handler.initial_sync()
            
            self.observer = Observer()
            self.observer.schedule(self.handler, str(self.vault_path), recursive=True)
            self.observer.start()
            
            logger.info("🔥 Obsidian Auto-Sync started successfully!")
            logger.info(f"Monitoring: {self.vault_path}")
            logger.info(f"API Endpoint: {self.api_url}")
            logger.info("Sync will happen automatically when files change...")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to start monitoring: {e}")
            return False
    
    def stop_monitoring(self):
        """Stop file system monitoring"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            logger.info("Obsidian Auto-Sync stopped")
    
    def get_sync_status(self):
        """Get current sync status"""
        if not self.handler:
            return {"status": "not_running"}
            
        conn = sqlite3.connect(self.handler.sync_db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT sync_status, COUNT(*) FROM file_sync GROUP BY sync_status')
        status_counts = dict(cursor.fetchall())
        
        cursor.execute('SELECT COUNT(*) FROM file_sync')
        total_files = cursor.fetchone()[0]
        
        cursor.execute('SELECT MAX(last_synced) FROM file_sync')
        last_sync = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "status": "running",
            "total_files": total_files,
            "synced": status_counts.get("synced", 0),
            "errors": status_counts.get("error", 0),
            "last_sync": last_sync
        }

def main():
    """Main function to run the sync system"""
    
    # Configuration - Update these paths for your system
    VAULT_PATH = input("Enter your Obsidian vault path: ").strip()
    API_URL = "https://c9226605-096b-4da8-b651-5f108cab0abe.preview.emergentagent.com"
    
    if not VAULT_PATH:
        logger.error("Vault path is required")
        return
    
    try:
        # Initialize and start sync system
        sync_system = ObsidianAutoSync(VAULT_PATH, API_URL)
        
        if sync_system.start_monitoring():
            logger.info("📝 Obsidian Vault Auto-Sync is now running!")
            logger.info("Press Ctrl+C to stop...")
            
            # Keep running until interrupted
            while True:
                time.sleep(10)
                status = sync_system.get_sync_status()
                if status["status"] == "running":
                    logger.info(f"Status: {status['synced']} synced, {status['errors']} errors, Last: {status['last_sync']}")
                
    except KeyboardInterrupt:
        logger.info("Stopping Obsidian Auto-Sync...")
        sync_system.stop_monitoring()
    except Exception as e:
        logger.error(f"Sync system error: {e}")

if __name__ == "__main__":
    main()