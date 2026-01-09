import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import subprocess
import os
import threading
import sys
import json
import glob
import datetime

DATA_FILE = "pake_history.json"

class PakeGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Pake CLI Management Studio")
        self.geometry("900x650")
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("Sidebar.TFrame", background="#2d2d2d")
        self.style.configure("Sidebar.TButton", background="#2d2d2d", foreground="white", borderwidth=0, anchor="w", padding=10)
        self.style.map("Sidebar.TButton", background=[("active", "#404040")])
        self.style.configure("Title.TLabel", font=("Segoe UI", 16, "bold"), background="#f0f0f0")
        self.style.configure("TLabel", background="#f0f0f0")
        self.style.configure("TCheckbutton", background="#f0f0f0")

        self.history_data = self.load_history()

        self.create_layout()
        self.show_builder()

    def load_history(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r") as f:
                    return json.load(f)
            except:
                return []
        return []

    def save_history(self, entry):
        # Check if identical entry exists
        for item in self.history_data:
            if item.get("name") == entry.get("name") and item.get("url") == entry.get("url"):
                item.update(entry)
                break
        else:
            self.history_data.insert(0, entry)
        
        with open(DATA_FILE, "w") as f:
            json.dump(self.history_data, f, indent=2)
        
        # Update history view if active
        if hasattr(self, 'history_view'):
            self.history_view.refresh()

    def create_layout(self):
        # Sidebar
        self.sidebar = ttk.Frame(self, style="Sidebar.TFrame", width=200)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)

        ttk.Label(self.sidebar, text="PAKE STUDIO", background="#2d2d2d", foreground="white", font=("Segoe UI", 14, "bold"), padding=20).pack(fill=tk.X)

        self.btn_builder = ttk.Button(self.sidebar, text="🔨  App Builder", style="Sidebar.TButton", command=self.show_builder)
        self.btn_builder.pack(fill=tk.X, pady=2)

        self.btn_builds = ttk.Button(self.sidebar, text="📦  Builds Manager", style="Sidebar.TButton", command=self.show_builds)
        self.btn_builds.pack(fill=tk.X, pady=2)

        self.btn_history = ttk.Button(self.sidebar, text="📚  My Apps (History)", style="Sidebar.TButton", command=self.show_history)
        self.btn_history.pack(fill=tk.X, pady=2)

        # Content Area
        self.content_area = ttk.Frame(self, style="TFrame")
        self.content_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def clear_content(self):
        for widget in self.content_area.winfo_children():
            widget.destroy()

    def show_builder(self):
        self.clear_content()
        BuilderView(self.content_area, self)

    def show_builds(self):
        self.clear_content()
        BuildsView(self.content_area, self)

    def show_history(self):
        self.clear_content()
        self.history_view = HistoryView(self.content_area, self)

class BuilderView:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        
        header = ttk.Label(parent, text="Create New App", style="Title.TLabel")
        header.pack(anchor=tk.W, padx=20, pady=20)

        container = ttk.Frame(parent)
        container.pack(fill=tk.BOTH, expand=True, padx=20)

        # Form Grid
        grid_frame = ttk.Frame(container)
        grid_frame.pack(fill=tk.X, pady=10)

        # Row 0: URL
        ttk.Label(grid_frame, text="Website URL (Required):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.url_var = tk.StringVar()
        ttk.Entry(grid_frame, textvariable=self.url_var, width=50).grid(row=0, column=1, columnspan=2, sticky=tk.W, pady=5)

        # Row 1: Name
        ttk.Label(grid_frame, text="App Name (Required):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.name_var = tk.StringVar()
        ttk.Entry(grid_frame, textvariable=self.name_var, width=50).grid(row=1, column=1, columnspan=2, sticky=tk.W, pady=5)

        # Row 2: Icon
        ttk.Label(grid_frame, text="Icon (URL or Path):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.icon_var = tk.StringVar()
        ttk.Entry(grid_frame, textvariable=self.icon_var, width=40).grid(row=2, column=1, sticky=tk.W, pady=5)
        ttk.Button(grid_frame, text="Browse", command=self.browse_icon).grid(row=2, column=2, sticky=tk.W, padx=5)

        # Row 3: ID (New Feature)
        ttk.Label(grid_frame, text="Bundle ID (Optional, for separation):").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.id_var = tk.StringVar()
        ttk.Entry(grid_frame, textvariable=self.id_var, width=50).grid(row=3, column=1, columnspan=2, sticky=tk.W, pady=5)
        ttk.Label(grid_frame, text="e.g., com.pake.myworkapp. Leave empty for default.", font=("Segoe UI", 8)).grid(row=4, column=1, columnspan=2, sticky=tk.W, pady=(0,5))

        # Row 4: Dimensions
        dim_frame = ttk.Frame(grid_frame)
        dim_frame.grid(row=5, column=0, columnspan=3, sticky=tk.W, pady=10)
        
        ttk.Label(dim_frame, text="Width:").pack(side=tk.LEFT)
        self.width_var = tk.StringVar(value="1200")
        ttk.Entry(dim_frame, textvariable=self.width_var, width=10).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(dim_frame, text="Height:").pack(side=tk.LEFT, padx=(15, 0))
        self.height_var = tk.StringVar(value="780")
        ttk.Entry(dim_frame, textvariable=self.height_var, width=10).pack(side=tk.LEFT, padx=5)

        # Row 5: Options
        opts_frame = ttk.Frame(grid_frame)
        opts_frame.grid(row=6, column=0, columnspan=3, sticky=tk.W, pady=10)
        
        self.fullscreen_var = tk.BooleanVar()
        ttk.Checkbutton(opts_frame, text="Fullscreen", variable=self.fullscreen_var).pack(side=tk.LEFT, padx=(0, 15))
        
        self.hide_title_bar_var = tk.BooleanVar()
        ttk.Checkbutton(opts_frame, text="Hide Title Bar", variable=self.hide_title_bar_var).pack(side=tk.LEFT)

        # Actions
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill=tk.X, padx=20)
        
        self.build_btn = ttk.Button(btn_frame, text="Build App", command=self.start_build)
        self.build_btn.pack(side=tk.RIGHT, pady=10)
        
        self.install_btn = ttk.Button(btn_frame, text="Install Dependencies", command=self.start_install)
        self.install_btn.pack(side=tk.RIGHT, padx=10, pady=10)

        # Log
        ttk.Label(parent, text="Output Log:").pack(anchor=tk.W, padx=20)
        self.log_text = tk.Text(parent, height=12, state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=(5, 20))

    def browse_icon(self):
        filename = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.ico;*.icns")])
        if filename:
            self.icon_var.set(filename)

    def log(self, message):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def start_install(self):
        self.toggle_buttons(False)
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        threading.Thread(target=self.run_install, daemon=True).start()

    def run_install(self):
        try:
            self.log("Installing dependencies with pnpm...")
            cmd = ["pnpm", "install"]
            if sys.platform == "win32":
                cmd = ["cmd", "/c"] + cmd
            
            self.run_process(cmd)
            self.log("Dependencies installed!")
        except Exception as e:
            self.log(f"Error: {e}")
        finally:
            self.toggle_buttons(True)

    def start_build(self):
        url = self.url_var.get().strip()
        name = self.name_var.get().strip()
        
        if not url or not name:
            messagebox.showerror("Error", "URL and Name are required!")
            return
            
        self.toggle_buttons(False)
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        
        threading.Thread(target=self.run_build, args=(url, name), daemon=True).start()

    def run_build(self, url, name):
        try:
             # Check for node_modules
            if not os.path.exists(os.path.join(os.getcwd(), "node_modules")):
                self.log("Error: node_modules not found. Building CLI might fail. Consider installing dependencies first.")

            # Check/Build CLI
            cli_path = os.path.join(os.getcwd(), "dist", "cli.js")
            if not os.path.exists(cli_path):
                self.log("Building CLI...")
                build_cmd = ["pnpm", "run", "cli:build"]
                if sys.platform == "win32":
                    build_cmd = ["cmd", "/c"] + build_cmd
                if self.run_process(build_cmd) != 0:
                     self.log("Failed to build CLI.")
                     return

            # Construct Command
            cmd = ["node", "dist/cli.js", url, "--name", name]
            
            if self.icon_var.get().strip():
                cmd.extend(["--icon", self.icon_var.get().strip()])
            
            if self.id_var.get().strip():
                cmd.extend(["--identifier", self.id_var.get().strip()])
                
            if self.width_var.get().strip():
                cmd.extend(["--width", self.width_var.get().strip()])
                
            if self.height_var.get().strip():
                cmd.extend(["--height", self.height_var.get().strip()])
                
            if self.fullscreen_var.get():
                cmd.append("--fullscreen")
                
            if self.hide_title_bar_var.get():
                cmd.append("--hide-title-bar")

            self.log(f"Executing: {' '.join(cmd)}")
            
            result_code = self.run_process(cmd)
            
            if result_code == 0:
                self.log("Build Success!")
                self.app.save_history({
                    "name": name,
                    "url": url,
                    "identifier": self.id_var.get().strip() or "Default",
                    "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                messagebox.showinfo("Success", "Build completed successfully!")
            else:
                self.log("Build Failed.")
                messagebox.showerror("Error", "Build failed!")

        except Exception as e:
            self.log(f"Exception: {str(e)}")
        finally:
            self.toggle_buttons(True)

    def run_process(self, cmd):
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        for line in process.stdout:
            self.log(line.strip())
        process.wait()
        return process.returncode

    def toggle_buttons(self, state):
        s = tk.NORMAL if state else tk.DISABLED
        self.build_btn.config(state=s)
        self.install_btn.config(state=s)

class BuildsView:
    def __init__(self, parent, app):
        self.parent = parent
        
        header = ttk.Label(parent, text="Available Builds", style="Title.TLabel")
        header.pack(anchor=tk.W, padx=20, pady=20)
        
        self.tree = ttk.Treeview(parent, columns=("Path"), show="headings")
        self.tree.heading("Path", text="File Location")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.tree.yview)
        scrollbar.place(relx=0.97, rely=0.2, relheight=0.7)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill=tk.X, padx=20, pady=20)
        
        ttk.Button(btn_frame, text="Open Folder", command=self.open_folder).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="Refresh", command=self.refresh).pack(side=tk.RIGHT)
        
        self.refresh()

    def refresh(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Common locations for Tauri builds
        patterns = [
            "src-tauri/target/release/bundle/msi/*.msi",
            "src-tauri/target/release/bundle/nsis/*.exe",
            "src-tauri/target/release/*.exe" 
        ]
        
        found = []
        for p in patterns:
            found.extend(glob.glob(os.path.join(os.getcwd(), p)))
            
        for f in found:
            self.tree.insert("", tk.END, values=(f,))

    def open_folder(self):
        selected = self.tree.selection()
        if selected:
            path = self.tree.item(selected[0])['values'][0]
            folder = os.path.dirname(path)
            os.startfile(folder)

class HistoryView:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        
        header = ttk.Label(parent, text="My Managed Apps", style="Title.TLabel")
        header.pack(anchor=tk.W, padx=20, pady=20)
        
        # Table
        cols = ("Name", "URL", "Date", "Identifier")
        self.tree = ttk.Treeview(parent, columns=cols, show="headings")
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
            
        self.tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.refresh()

    def refresh(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for entry in self.app.history_data:
            self.tree.insert("", tk.END, values=(
                entry.get("name"), 
                entry.get("url"), 
                entry.get("date"),
                entry.get("identifier")
            ))

if __name__ == "__main__":
    app = PakeGUI()
    app.mainloop()
