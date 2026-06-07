import os
import shutil
import tkinter as tk
from tkinter import messagebox, ttk
import re
import base64
from datetime import datetime

class ClaudeMigratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Claude Desktop Session Migrator")
        self.root.geometry("750x600")
        
        # Base Path Detection (Microsoft Store Version)
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

    def log(self, message):
        """Append a message to the status log."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_area.config(state="normal")
        self.log_area.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_area.see(tk.END)
        self.log_area.config(state="disabled")
        self.root.update_idletasks()

    def resolve_names(self):
        """Try to map UUIDs to emails by scanning Claude logs."""
        log_path = os.path.join(self.base_path, 'logs', 'main.log')
        if not os.path.exists(log_path):
            self.log("Warning: main.log not found. Cannot resolve account names.")
            return
        
        self.log("Scanning logs for account identities...")
        mappings = {}
        try:
            with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                relevant_lines = lines[-20000:]
                
                current_uuid = None
                for i, line in enumerate(relevant_lines):
                    match_acc = re.search(r"accountId=([a-f0-9-]+)", line)
                    if match_acc:
                        current_uuid = match_acc.group(1)
                    
                    match_id = re.search(r"uuid: [a-f0-9-]+ -> ([a-f0-9-]+)", line)
                    if match_id:
                        current_uuid = match_id.group(1)

                    magic_match = re.search(r"magic-link#[a-f0-9]+:([A-Za-z0-9+/=]+)", line)
                    if magic_match and current_uuid:
                        try:
                            email = base64.b64decode(magic_match.group(1)).decode('utf-8')
                            if '@' in email:
                                mappings[current_uuid] = email
                        except: pass
                            
                    if "'CLAUDE_CODE_USER_EMAIL'," in line and i + 1 < len(relevant_lines) and current_uuid:
                        email_match = re.search(r"'([^']+@([^']+))'", relevant_lines[i+1])
                        if email_match:
                            mappings[current_uuid] = email_match.group(1)
        except Exception as e:
            self.log(f"Error during log scan: {e}")
        
        self.uuid_to_name = mappings
        self.log(f"Found {len(mappings)} named accounts.")

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="25")
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="Claude Desktop Session Migrator", font=("Helvetica", 16, "bold")).pack(pady=10)
        
        # Path Check
        exists = os.path.exists(self.base_path)
        path_color = "green" if exists else "red"
        ttk.Label(main_frame, text=f"Claude Data Directory: {'[FOUND]' if exists else '[NOT FOUND]'}", 
                  foreground=path_color, font=("Helvetica", 10)).pack()

        # Selection
        selection_frame = ttk.LabelFrame(main_frame, text=" Account Selection ", padding="15")
        selection_frame.pack(fill="x", pady=20)

        ttk.Label(selection_frame, text="Source (Old Account):").grid(row=0, column=0, sticky="w", pady=5)
        self.source_var = tk.StringVar()
        self.source_combo = ttk.Combobox(selection_frame, textvariable=self.source_var, width=70, state="readonly")
        self.source_combo.grid(row=1, column=0, pady=(0, 10))

        ttk.Label(selection_frame, text="Destination (New Account):").grid(row=2, column=0, sticky="w", pady=5)
        self.dest_var = tk.StringVar()
        self.dest_combo = ttk.Combobox(selection_frame, textvariable=self.dest_var, width=70, state="readonly")
        self.dest_combo.grid(row=3, column=0)

        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Refresh Lists", command=self.refresh).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="START MIGRATION", command=self.migrate).pack(side=tk.LEFT, padx=10)

        # Log Area
        ttk.Label(main_frame, text="Migration Log:", font=("Helvetica", 9, "bold")).pack(anchor="w", pady=(10, 0))
        self.log_area = tk.Text(main_frame, height=12, font=("Consolas", 9), state="disabled", bg="#1e1e1e", fg="#d4d4d4")
        self.log_area.pack(fill="both", expand=True, pady=5)
        
        # Scrollbar for log
        scrollbar = ttk.Scrollbar(self.log_area, command=self.log_area.yview)
        self.log_area.config(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill="y")

    def refresh(self):
        self.log_area.config(state="normal")
        self.log_area.delete("1.0", tk.END)
        self.log_area.config(state="disabled")
        
        self.resolve_names()
        session_path = os.path.join(self.base_path, 'claude-code-sessions')
        folders = [d for d in os.listdir(session_path) if os.path.isdir(os.path.join(session_path, d))] if os.path.exists(session_path) else []
        
        display_list = [f"{self.uuid_to_name.get(f, 'Unknown Account')} ({f})" for f in folders]
        self.source_combo['values'] = display_list
        self.dest_combo['values'] = display_list
        
        if display_list:
            self.source_combo.current(0)
            if len(display_list) > 1: self.dest_combo.current(len(display_list)-1)
        
        self.log("Ready. Select accounts and click Start Migration.")

    def migrate(self):
        src_raw, dst_raw = self.source_var.get(), self.dest_var.get()
        if not src_raw or not dst_raw: return
        
        src_uuid = re.search(r"\(([a-f0-9-]+)\)$", src_raw).group(1)
        dst_uuid = re.search(r"\(([a-f0-9-]+)\)$", dst_raw).group(1)

        if src_uuid == dst_uuid:
            messagebox.showerror("Error", "Source and Destination accounts are the same.")
            return

        if not messagebox.askyesno("Confirm", f"Merge all Code Sessions from:\n{src_raw}\n\nTo:\n{dst_raw}?"):
            return

        self.log(f"Starting migration: {src_uuid} -> {dst_uuid}")
        try:
            total_copied = 0
            for s_type in ['claude-code-sessions', 'local-agent-mode-sessions']:
                s_base = os.path.join(self.base_path, s_type, src_uuid)
                d_base = os.path.join(self.base_path, s_type, dst_uuid)
                
                if not os.path.exists(s_base):
                    self.log(f"Skipping {s_type} (no source data).")
                    continue
                
                self.log(f"Processing {s_type}...")
                for org in os.listdir(s_base):
                    s_org, d_org = os.path.join(s_base, org), os.path.join(d_base, org)
                    if os.path.isdir(s_org):
                        os.makedirs(d_org, exist_ok=True)
                        for f in os.listdir(s_org):
                            if f.endswith('.json'):
                                shutil.copy2(os.path.join(s_org, f), os.path.join(d_org, f))
                                self.log(f"  + Copied: {f[:20]}...")
                                total_copied += 1
            
            self.log(f"MIGRATION COMPLETE. {total_copied} sessions merged.")
            messagebox.showinfo("Success", f"Successfully migrated {total_copied} sessions.\n\nRestart Claude Desktop to see the changes.")
        except Exception as e:
            self.log(f"FATAL ERROR: {str(e)}")
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = ClaudeMigratorApp(root)
    root.mainloop()
