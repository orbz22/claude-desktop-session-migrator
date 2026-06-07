# Claude Desktop Session Migrator

A simple Python GUI tool to migrate and merge "Code Sessions" and "Local Agent Mode" chats between different accounts in Claude Desktop.

## 📌 Why this exists?
Claude Desktop stores developer sessions (Code Sessions) locally on your machine, partitioned by your Account UUID. When you switch accounts, your previous code sessions are hidden because Claude looks in a new, empty folder. 

This tool maps those cryptic UUIDs to your email addresses (by scanning local logs) and allows you to copy/merge your session history from one account to another with a single click.

## 🚀 Features
- **Automatic Account Detection:** Scans Claude's local data directory automatically.
- **Identity Resolution:** Maps UUIDs to email addresses using local logs so you know which account is which.
- **Merge & Update:** Copies `.json` session files from source to destination.
- **Safety First:** Performs a copy (not a move), ensuring your original data stays intact.

## 🛠️ Requirements
- Windows 10/11
- Python 3.x
- Claude Desktop (Microsoft Store/Standard Version)

## 📖 How to Use
1. **Close Claude Desktop** completely (check your system tray).
2. Run the script:
   ```powershell
   python claude_session_migrator.py
   ```
3. Select your **Source Account** (the one with the data).
4. Select your **Destination Account** (the one you want the data moved to).
5. Click **Migrate Sessions**.
6. Re-open Claude Desktop.

## ⚠️ Disclaimer
This tool is for **local session data only** (Code Sessions/Agent Mode). Regular cloud-synced chats are managed by Anthropic and are not affected by this tool. Always ensure you have a backup of your `%AppData%` folder before performing migrations.

---
*Not affiliated with Anthropic.*
