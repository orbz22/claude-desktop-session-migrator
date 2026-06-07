import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import re
import base64

class ClaudeMigratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Claude Desktop Session Migrator")
        self.root.geometry("700x450")
        
        # Base Path Detection
        self.base_path = os.path.join(
            os.environ.get('LOCALAPPDATA', ''), 
            'Packages', 
            'Claude_pzs8sxrjxfjjc', 
            'LocalCache', 
            'Roaming', 
            'Claude'
        )
        
        self.uuid_to_name = {}
        self.setup_ui()
        self.refresh()

    def resolve_names(self):
        """Try to map UUIDs to emails/names from logs."""
        log_path = os.path.join(self.base_path, 'logs', 'main.log')
        if not os.path.exists(log_path):
            return
        
        mappings = {}
        try:
            with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                # Read last 10000 lines for efficiency
                lines = f.readlines()
                relevant_lines = lines[-10000:]
                
                current_uuid = None
                for i, line in enumerate(relevant_lines):
                    # Clue 1: Identity changed lines
                    match = re.search(r"uuid: [a-f0-9-]+ -> ([a-f0-9-]+)", line)
                    if match:
                        current_uuid = match.group(1)
                    
                    # Clue 2: accountId= in Initialization succeeded
                    match_acc = re.search(r"accountId=([a-f0-9-]+)", line)
                    if match_acc:
                        current_uuid = match_acc.group(1)

                    # Clue 3: Magic link with base64 email
                    magic_match = re.search(r"magic-link#[a-f0-9]+:([A-Za-z0-9+/=]+)", line)
                    if magic_match and current_uuid:
                        try:
                            b64_email = magic_match.group(1)
                            email = base64.b64decode(b64_email).decode('utf-8')
                            if '@' in email:
                                mappings[current_uuid] = email
                        except:
                            pass
                            
                    # Clue 4: CLAUDE_CODE_USER_EMAIL in sdkOptions
                    if "'CLAUDE_CODE_USER_EMAIL'," in line and i + 1 < len(relevant_lines) and current_uuid:
                        next_line = relevant_lines[i+1]
                        email_match = re.search(r"'([^']+@([^']+))'", next_line)
                        if email_match:
                            mappings[current_uuid] = email_match.group(1)

        except Exception as e:
            print(f"Error resolving names: {e}")
        
        self.uuid_to_name = mappings

    def setup_ui(self):
        style = ttk.Style()
        style.configure("TButton", padding=6)
        
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="Claude Desktop Session Migrator", font=("Helvetica", 16, "bold")).pack(pady=10)
        
        # Path Status
        path_status = "Path Detected" if os.path.exists(self.base_path) else "Path NOT Found"
        ttk.Label(main_frame, text=f"Base Path: {path_status}", foreground="green" if os.path.exists(self.base_path) else "red").pack()

        # Source Selection
        ttk.Label(main_frame, text="Select Source Account (Old):").pack(pady=(15, 0))
        self.source_var = tk.StringVar()
        self.source_combo = ttk.Combobox(main_frame, textvariable=self.source_var, width=80)
        self.source_combo.pack(pady=5)

        # Destination Selection
        ttk.Label(main_frame, text="Select Destination Account (New):").pack(pady=(15, 0))
        self.dest_var = tk.StringVar()
        self.dest_combo = ttk.Combobox(main_frame, textvariable=self.dest_var, width=80)
        self.dest_combo.pack(pady=5)

        # Action Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=20)
        
        ttk.Button(btn_frame, text="Refresh & Resolve Names", command=self.refresh).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Migrate Sessions", command=self.migrate).pack(side=tk.LEFT, padx=5)

        ttk.Label(main_frame, text="Note: Close Claude Desktop before migrating.", font=("Helvetica", 8, "italic")).pack(pady=10)

    def get_display_list(self, folders):
        display_list = []
        for f in folders:
            name = self.uuid_to_name.get(f, "Unknown Account")
            display_list.append(f"{name} ({f})")
        return display_list

    def extract_uuid(self, display_string):
        match = re.search(r"\(([a-f0-9-]+)\)$", display_string)
        return match.group(1) if match else display_string

    def get_claude_account_folders(self):
        session_path = os.path.join(self.base_path, 'claude-code-sessions')
        if not os.path.exists(session_path):
            return []
        return [d for d in os.listdir(session_path) if os.path.isdir(os.path.join(session_path, d))]

    def refresh(self):
        self.resolve_names()
        folders = self.get_claude_account_folders()
        display_list = self.get_display_list(folders)
        
        self.source_combo['values'] = display_list
        self.dest_combo['values'] = display_list
        
        # Auto-select if there are values
        if display_list:
            if not self.source_var.get(): self.source_combo.current(0)
            if len(display_list) > 1 and not self.dest_var.get(): self.dest_combo.current(1)

    def migrate(self):
        src_display = self.source_var.get()
        dst_display = self.dest_var.get()

        if not src_display or not dst_display:
            messagebox.showwarning("Error", "Please select both source and destination folders.")
            return
        
        src = self.extract_uuid(src_display)
        dst = self.extract_uuid(dst_display)

        if src == dst:
            messagebox.showwarning("Error", "Source and Destination cannot be the same.")
            return

        confirm = messagebox.askyesno("Confirm Migration", f"Copy sessions from:\n{src_display}\n\nTo:\n{dst_display}?\n\nThis will merge the histories.")
        if not confirm:
            return

        try:
            moved_count = 0
            session_types = ['claude-code-sessions', 'local-agent-mode-sessions']
            
            for s_type in session_types:
                src_base = os.path.join(self.base_path, s_type, src)
                dst_base = os.path.join(self.base_path, s_type, dst)
                
                if not os.path.exists(src_base): continue
                
                # Check for sub-directories (org IDs)
                for sub_dir in os.listdir(src_base):
                    full_src = os.path.join(src_base, sub_dir)
                    if os.path.isdir(full_src):
                        full_dst = os.path.join(dst_base, sub_dir)
                        os.makedirs(full_dst, exist_ok=True)
                        
                        for item in os.listdir(full_src):
                            s_file = os.path.join(full_src, item)
                            d_file = os.path.join(full_dst, item)
                            if os.path.isfile(s_file) and item.endswith('.json'):
                                shutil.copy2(s_file, d_file)
                                moved_count += 1
            
            messagebox.showinfo("Success", f"Successfully migrated {moved_count} session files.\n\nPlease restart Claude Desktop.")
        except Exception as e:
            messagebox.showerror("Migration Failed", f"An error occurred: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ClaudeMigratorApp(root)
    root.mainloop()
