#!/usr/bin/env python3
"""
Quick start/stop control for Obsidian sync
"""

import json
import sys
from pathlib import Path

def load_config():
    config_file = Path.home() / ".obsidian_sync_config.json"
    if config_file.exists():
        with open(config_file, 'r') as f:
            return json.load(f)
    return None

def start_sync():
    config = load_config()
    if not config:
        print("❌ No configuration found. Please run setup first:")
        print("   python /app/setup_obsidian_sync.py")
        return
    
    print("🔥 Starting Obsidian Auto-Sync...")
    sys.path.insert(0, '/app')
    from obsidian_sync_system import ObsidianAutoSync
    import time
    
    try:
        sync_system = ObsidianAutoSync(config["vault_path"], config["api_url"])
        
        if sync_system.start_monitoring():
            print(f"📁 Monitoring: {config['vault_path']}")
            print("🔄 Auto-sync is now running!")
            print("Press Ctrl+C to stop...")
            
            while True:
                time.sleep(60)
                status = sync_system.get_sync_status()
                print(f"📊 {status.get('synced', 0)} synced, {status.get('errors', 0)} errors")
                
    except KeyboardInterrupt:
        print("\n🛑 Stopping sync...")
        sync_system.stop_monitoring()
        print("✅ Stopped")

if __name__ == "__main__":
    start_sync()