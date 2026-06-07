# 🚀 Claude Desktop Session Migrator

[![GitHub license](https://img.shields.io/github/license/mashape/apistatus.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-windows-lightgrey.svg)](https://www.microsoft.com/windows)

**Rescue your "missing" Code Sessions and Agent chats after switching accounts in Claude Desktop.**

Claude Desktop stores your advanced developer sessions (Agent Mode/Cowork) locally on your machine. These files are locked to your specific Account ID (UUID). When you switch accounts, your history seemingly "disappears" because Claude looks in a new, empty folder.

This tool acts as a bridge, mapping those cryptic IDs to your email addresses and allowing you to **copy or merge** your session history between accounts with one click.

---

## ✨ Features

- **🔍 Smart Account Discovery:** Automatically detects all Claude accounts logged into your machine.
- **📧 Email Mapping:** Scans local logs to show you exactly which email belongs to which ID.
- **📂 Deep Migration:** Moves both `claude-code-sessions` and `local-agent-mode-sessions` (Cowork).
- **🛡️ Safety First:** Uses a copy-merge strategy. It never deletes your original data.
- **📊 Real-time Logs:** See exactly which files are being moved in the built-in status window.

---

## 📸 Preview
*(Add a screenshot here once you run the app!)*

---

## 🛠️ Installation

### Option 1: Run from Source (Recommended for Devs)
1. Clone the repo:
   ```bash
   git clone https://github.com/YOUR_USERNAME/claude-desktop-session-migrator.git
   cd claude-desktop-session-migrator
   ```
2. Install requirements (Standard library only, but good for environment setup):
   ```bash
   pip install -r requirements.txt
   ```
3. Run the app:
   ```bash
   python claude_session_migrator.py
   ```

### Option 2: Download Executable (.exe)
1. Go to the [Releases](https://github.com/YOUR_USERNAME/claude-desktop-session-migrator/releases) page.
2. Download `ClaudeMigrator.exe`.
3. Run it directly! (No Python required).

---

## 📖 How to Use

1. **CRITICAL:** Fully close Claude Desktop (Check the System Tray/Task Manager).
2. Open **Claude Desktop Session Migrator**.
3. **Source Account:** Select the account that *has* your chats.
4. **Destination Account:** Select the account you want to *move* them to.
5. Click **START MIGRATION**.
6. Re-open Claude Desktop. Your chats will now appear in the sidebar!

---

## ❓ FAQ

**Q: Does this sync my regular chats?**  
A: No. Regular chats are cloud-synced by Anthropic. This tool is specifically for **Code Sessions** and **Agent/Cowork** sessions that are stored locally.

**Q: Will this delete my old chats?**  
A: Never. The tool uses `shutil.copy2`, which creates a duplicate. Your original files remain untouched.

**Q: Can I merge two accounts permanently?**  
A: This tool performs a "snapshot" copy. If you send new messages in Account A, you'll need to run the tool again to see them in Account B.

---

## ⚠️ Warning & Disclaimer

- **Data Privacy:** This tool scans your local Claude logs to find your email address. This data **never** leaves your computer.
- **Backups:** While this tool only copies data, it's always wise to backup your `%AppData%\Local\Packages\Claude_pzs8sxrjxfjjc` folder before manual migrations.
- **Experimental:** This tool is not affiliated with Anthropic. Use it at your own risk.

---

## 🤝 Contributing
Found a bug? Have a feature request? Feel free to open an Issue or a Pull Request!

## 📜 License
MIT License. See `LICENSE` for details.
