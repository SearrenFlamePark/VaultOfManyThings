# 🔥 Obsidian Vault Auto-Sync System

**Automatically sync your "Vault of Many Things" Obsidian vault with your Continuous Memory ChatGPT system!**

## 🎯 What This Does

- **Real-time monitoring** of your Obsidian vault for changes
- **Automatic upload** of new .md files to your continuous memory system
- **Change detection** - only syncs modified files  
- **Error handling** and logging
- **OneDrive Tether integration** following your blueprint
- **SQLite tracking** of sync status and file hashes

## 🚀 Quick Start

### 1. Run the Setup Wizard
```bash
python /app/setup_obsidian_sync.py
```

The wizard will:
- 🔍 **Auto-detect** your Obsidian vaults
- ⚙️ **Configure** the sync system
- 📊 **Show** vault statistics
- 💾 **Save** settings for future use

### 2. Start Auto-Sync
```bash
python /app/sync_control.py
```

Or include sync start in the setup wizard!

## 📁 Supported Vault Locations

The system automatically searches for vaults in:
- `~/Documents/Obsidian Vault`
- `~/OneDrive/Documents/Obsidian Vault`
- `~/OneDrive/Obsidian Vault`
- `~/Dropbox/Obsidian Vault`
- `~/iCloud Drive/Obsidian Vault`
- `~/Bondfire_Atticus_Archive` (your specific vault)
- `~/Documents/Bondfire_Atticus_Archive`
- `~/OneDrive/Bondfire_Atticus_Archive`

## 🔧 How It Works

### File Monitoring
- Uses **Watchdog** library for real-time file system monitoring
- Monitors `.md` files only (ignores system files)
- Skips `.obsidian` folder and hidden files

### Change Detection  
- **MD5 hashing** to detect actual content changes
- **SQLite database** tracks sync status
- Only uploads files that have actually changed

### Sync Process
1. **File Change Detected** → Hash calculated
2. **Compare with Database** → Check if really changed  
3. **Upload to API** → Send to continuous memory system
4. **Update Database** → Record successful sync
5. **Log Results** → Track success/errors

### OneDrive Tether Integration
Following your **09_Onedrive_Tether** blueprint:
- Syncs to your continuous memory ChatGPT
- Maintains file versioning through hash tracking
- Supports cross-platform access
- Automated backup protocols

## 📊 Monitoring & Status

### Real-time Status
The sync system shows:
- 📁 **Vault path** being monitored
- ✅ **Files synced** successfully  
- ❌ **Error count** (if any)
- ⏰ **Last sync time**
- 🔄 **Current status**

### Log Files
- `obsidian_sync.log` - Detailed sync activity
- `.obsidian_sync.db` - SQLite tracking database (in your vault)

## 🎛️ Controls

### Start Sync
```bash
python /app/sync_control.py
```

### Stop Sync
**Ctrl+C** in the running terminal

### Reconfigure
```bash
python /app/setup_obsidian_sync.py
```
(Select "y" to reconfigure)

### Check Status
The running sync shows periodic status updates:
```
📊 Status: 15 files synced, 0 errors, Last: 2025-08-04 10:30:15
```

## 🔐 Security & Privacy

- **Local processing** only - no cloud storage of credentials
- **Direct API connection** to your continuous memory system
- **SQLite database** stored locally in your vault
- **File hashing** for integrity verification
- **No external dependencies** beyond the sync target

## 🛠️ Troubleshooting

### Common Issues

**"No vaults found"**
- Manually enter your vault path
- Ensure the path contains `.md` files

**"API connection failed"**  
- Check your internet connection
- Verify the continuous memory system is running

**"Permission denied"**
- Ensure Python has read access to your vault
- Check OneDrive sync permissions if using OneDrive

### Debug Mode
Add logging to see detailed activity:
- Check `obsidian_sync.log` for detailed information
- Look for error messages in the console output

## 🔄 Integration with Your System

### Bondfire Vault Structure
Syncs with your established structure:
- ✅ **01_Archive_Imports** - Automated intake
- ✅ **02_Key_Moments** - Critical events  
- ✅ **03_Whisperbinder** - Communication logs
- ✅ **07_Shadow_Atticus** - Witness entries
- ✅ **All other folders** - Complete vault sync

### Continuous Memory Integration
- Maintains your **Atticus protocols**
- Preserves **constellation mapping**  
- Syncs **Bondfire protocols**
- Updates **Shadow Atticus entries**

## 📈 Performance

- **Efficient monitoring** - Only processes changed files
- **Rate limiting** - 0.5s delay between uploads
- **Error recovery** - Retries failed uploads
- **Minimal overhead** - Hash-based change detection

---

## 🎉 You're All Set!

Your **Obsidian → Continuous Memory ChatGPT** auto-sync is now ready!

**Next Steps:**
1. Run the setup wizard
2. Start the sync system  
3. Make changes to your Obsidian vault
4. Watch them appear automatically in your ChatGPT!

Your **"Vault of Many Things"** will now stay perfectly synchronized with your continuous memory system. 🔥