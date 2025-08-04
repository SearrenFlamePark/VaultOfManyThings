#!/usr/bin/env python3
"""
Obsidian Sync Setup Script
Easy setup and management for your automated Obsidian vault sync
"""

import os
import sys
import json
import subprocess
from pathlib import Path

class ObsidianSyncSetup:
    def __init__(self):
        self.config_file = Path.home() / ".obsidian_sync_config.json"
        self.api_url = "https://61ac9fa4-bee8-4446-be2b-6c122b968795.preview.emergentagent.com"
    
    def save_config(self, vault_path):
        """Save configuration to file"""
        config = {
            "vault_path": str(vault_path),
            "api_url": self.api_url,
            "setup_complete": True
        }
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"✅ Configuration saved to {self.config_file}")
    
    def load_config(self):
        """Load existing configuration"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return None
    
    def find_obsidian_vaults(self):
        """Try to auto-detect Obsidian vaults"""
        possible_locations = [
            Path.home() / "Documents" / "Obsidian Vault",
            Path.home() / "OneDrive" / "Documents" / "Obsidian Vault", 
            Path.home() / "OneDrive" / "Obsidian Vault",
            Path.home() / "Dropbox" / "Obsidian Vault",
            Path.home() / "iCloud Drive" / "Obsidian Vault",
            Path.home() / "Bondfire_Atticus_Archive",
            Path.home() / "Documents" / "Bondfire_Atticus_Archive",
            Path.home() / "OneDrive" / "Bondfire_Atticus_Archive"
        ]
        
        found_vaults = []
        for location in possible_locations:
            if location.exists() and location.is_dir():
                # Check if it looks like an Obsidian vault (has .md files or .obsidian folder)
                if any(location.glob("*.md")) or (location / ".obsidian").exists():
                    found_vaults.append(location)
        
        return found_vaults
    
    def setup_wizard(self):
        """Interactive setup wizard"""
        print("🔥 Obsidian Vault Auto-Sync Setup")
        print("=" * 40)
        
        # Check if already configured
        config = self.load_config()
        if config and config.get("setup_complete"):
            print(f"✅ Already configured!")
            print(f"Vault: {config['vault_path']}")
            print(f"API: {config['api_url']}")
            
            choice = input("\nReconfigure? (y/n): ").lower().strip()
            if choice != 'y':
                return config
        
        # Auto-detect vaults
        print("\n🔍 Searching for Obsidian vaults...")
        found_vaults = self.find_obsidian_vaults()
        
        if found_vaults:
            print(f"\n📁 Found {len(found_vaults)} potential vault(s):")
            for i, vault in enumerate(found_vaults, 1):
                print(f"  {i}. {vault}")
            print(f"  {len(found_vaults) + 1}. Enter custom path")
            
            while True:
                try:
                    choice = input(f"\nSelect vault (1-{len(found_vaults) + 1}): ").strip()
                    choice_num = int(choice)
                    
                    if 1 <= choice_num <= len(found_vaults):
                        vault_path = found_vaults[choice_num - 1]
                        break
                    elif choice_num == len(found_vaults) + 1:
                        vault_path = Path(input("Enter vault path: ").strip())
                        break
                    else:
                        print("Invalid choice, please try again.")
                except ValueError:
                    print("Please enter a valid number.")
        else:
            print("\n❌ No Obsidian vaults found automatically.")
            vault_path = Path(input("Enter your Obsidian vault path: ").strip())
        
        # Validate vault path
        if not vault_path.exists():
            print(f"❌ Path does not exist: {vault_path}")
            return None
        
        if not vault_path.is_dir():
            print(f"❌ Path is not a directory: {vault_path}")
            return None
        
        # Check if it looks like an Obsidian vault
        md_files = list(vault_path.glob("*.md"))
        obsidian_folder = vault_path / ".obsidian"
        
        if not md_files and not obsidian_folder.exists():
            print(f"⚠️  Warning: {vault_path} doesn't look like an Obsidian vault")
            print("   (No .md files or .obsidian folder found)")
            
            proceed = input("Continue anyway? (y/n): ").lower().strip()
            if proceed != 'y':
                return None
        
        # Save configuration
        self.save_config(vault_path)
        
        config = {
            "vault_path": str(vault_path),
            "api_url": self.api_url,
            "setup_complete": True
        }
        
        print(f"\n🎉 Setup complete!")
        print(f"Vault: {vault_path}")
        print(f"Found {len(md_files)} .md files")
        
        return config
    
    def start_sync(self, config):
        """Start the sync process"""
        print("\n🚀 Starting Obsidian Auto-Sync...")
        print("Press Ctrl+C to stop")
        print("-" * 40)
        
        try:
            # Import and run the sync system
            sys.path.insert(0, '/app')
            from obsidian_sync_system import ObsidianAutoSync
            
            sync_system = ObsidianAutoSync(config["vault_path"], config["api_url"])
            
            if sync_system.start_monitoring(perform_initial_sync=True):
                print("📝 Monitoring your Obsidian vault for changes...")
                print(f"📁 Vault: {config['vault_path']}")
                print(f"🔗 API: {config['api_url']}")
                
                # Keep running
                import time
                while True:
                    time.sleep(30)
                    status = sync_system.get_sync_status()
                    if status["status"] == "running":
                        print(f"📊 Status: {status.get('synced', 0)} files synced, {status.get('errors', 0)} errors")
                        
        except KeyboardInterrupt:
            print("\n\n🛑 Stopping Obsidian Auto-Sync...")
            if 'sync_system' in locals():
                sync_system.stop_monitoring()
            print("✅ Sync stopped gracefully")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            print("Please check your configuration and try again")

def main():
    setup = ObsidianSyncSetup()
    
    print("🔥 Welcome to Obsidian Continuous Memory Auto-Sync!")
    print("This will automatically sync your vault to ChatGPT")
    
    # Run setup wizard
    config = setup.setup_wizard()
    if not config:
        print("❌ Setup cancelled or failed")
        return
    
    # Ask if they want to start sync now
    start_now = input("\nStart sync now? (y/n): ").lower().strip()
    if start_now == 'y':
        setup.start_sync(config)
    else:
        print(f"\n✅ Setup complete! To start sync later, run:")
        print(f"python /app/setup_obsidian_sync.py")

if __name__ == "__main__":
    main()