import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import subprocess
import os
import threading
import sys

class PakeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Pake CLI Builder (Windows)")
        self.root.geometry("600x550")
        
        self.create_widgets()
        
    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # URL
        ttk.Label(main_frame, text="Website URL (Required):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.url_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.url_var, width=50).grid(row=0, column=1, columnspan=2, sticky=tk.W, pady=5)
        
        # Name
        ttk.Label(main_frame, text="App Name (Required):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.name_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.name_var, width=50).grid(row=1, column=1, columnspan=2, sticky=tk.W, pady=5)
        
        # Icon
        ttk.Label(main_frame, text="Icon (URL or Path):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.icon_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.icon_var, width=40).grid(row=2, column=1, sticky=tk.W, pady=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_icon).grid(row=2, column=2, sticky=tk.W, padx=5)
        
        # Dimensions
        dim_frame = ttk.Frame(main_frame)
        dim_frame.grid(row=3, column=0, columnspan=3, sticky=tk.W, pady=10)
        
        ttk.Label(dim_frame, text="Width:").pack(side=tk.LEFT)
        self.width_var = tk.StringVar(value="1200")
        ttk.Entry(dim_frame, textvariable=self.width_var, width=10).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(dim_frame, text="Height:").pack(side=tk.LEFT, padx=(15, 0))
        self.height_var = tk.StringVar(value="780")
        ttk.Entry(dim_frame, textvariable=self.height_var, width=10).pack(side=tk.LEFT, padx=5)
        
        # Options
        self.fullscreen_var = tk.BooleanVar()
        ttk.Checkbutton(main_frame, text="Start in Fullscreen", variable=self.fullscreen_var).grid(row=4, column=0, columnspan=3, sticky=tk.W, pady=2)
        
        self.hide_title_bar_var = tk.BooleanVar()
        ttk.Checkbutton(main_frame, text="Hide Title Bar", variable=self.hide_title_bar_var).grid(row=5, column=0, columnspan=3, sticky=tk.W, pady=2)
        
        # Build Button
        self.build_btn = ttk.Button(main_frame, text="Build App", command=self.start_build)
        self.build_btn.grid(row=6, column=0, columnspan=2, pady=20, sticky=tk.E)

        # Install Dependencies Button
        self.install_btn = ttk.Button(main_frame, text="Install Dependencies", command=self.start_install)
        self.install_btn.grid(row=6, column=2, pady=20, sticky=tk.W, padx=5)
        
        # Output Log
        ttk.Label(main_frame, text="Output Log:").grid(row=7, column=0, sticky=tk.W)
        self.log_text = tk.Text(main_frame, height=10, width=70, state=tk.DISABLED)
        self.log_text.grid(row=8, column=0, columnspan=3, pady=5)
        
        # Scrollbar for log
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.log_text.yview)
        scrollbar.grid(row=8, column=3, sticky="ns")
        self.log_text.configure(yscrollcommand=scrollbar.set)

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
        self.install_btn.config(state=tk.DISABLED)
        self.build_btn.config(state=tk.DISABLED)
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
            
            if process.returncode == 0:
                self.log("Dependencies installed successfully!")
                messagebox.showinfo("Success", "Dependencies installed successfully!")
            else:
                self.log(f"Installation failed with return code {process.returncode}")
                messagebox.showerror("Error", "Installation failed!")

        except Exception as e:
            self.log(f"An error occurred: {str(e)}")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
        finally:
            self.root.after(0, lambda: self.install_btn.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.build_btn.config(state=tk.NORMAL))

    def start_build(self):
        url = self.url_var.get().strip()
        name = self.name_var.get().strip()
        
        if not url or not name:
            messagebox.showerror("Error", "URL and Name are required!")
            return
            
        self.build_btn.config(state=tk.DISABLED)
        self.install_btn.config(state=tk.DISABLED)
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        
        threading.Thread(target=self.run_build, args=(url, name), daemon=True).start()

    def run_build(self, url, name):
        try:
            # Check for node_modules
            if not os.path.exists(os.path.join(os.getcwd(), "node_modules")):
                self.log("Error: node_modules not found. Please click 'Install Dependencies' first.")
                messagebox.showerror("Error", "Dependencies not installed. Please click 'Install Dependencies' first.")
                return

            # Check if dist/cli.js exists
            cli_path = os.path.join(os.getcwd(), "dist", "cli.js")
            if not os.path.exists(cli_path):
                self.log("Error: dist/cli.js not found. Running 'pnpm run cli:build' first...")
                # Try to build the CLI first
                build_cmd = ["pnpm", "run", "cli:build"]
                if sys.platform == "win32":
                    build_cmd = ["cmd", "/c"] + build_cmd
                
                proc = subprocess.Popen(build_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                for line in proc.stdout:
                    self.log(line.strip())
                proc.wait()
                
                if proc.returncode != 0:
                    self.log("Failed to build CLI.")
                    self.root.after(0, lambda: self.build_btn.config(state=tk.NORMAL))
                    self.root.after(0, lambda: self.install_btn.config(state=tk.NORMAL))
                    return

            # Construct command
            cmd = ["node", "dist/cli.js", url, "--name", name]
            
            if self.icon_var.get().strip():
                cmd.extend(["--icon", self.icon_var.get().strip()])
                
            if self.width_var.get().strip():
                cmd.extend(["--width", self.width_var.get().strip()])
                
            if self.height_var.get().strip():
                cmd.extend(["--height", self.height_var.get().strip()])
                
            if self.fullscreen_var.get():
                cmd.append("--fullscreen")
                
            if self.hide_title_bar_var.get():
                cmd.append("--hide-title-bar")

            self.log(f"Running command: {' '.join(cmd)}")
            
            # Run command
            if sys.platform == "win32":
                # Use shell=True for Windows to find node in path easily, or just rely on subprocess
                # But for node it should be fine.
                pass

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
            
            if process.returncode == 0:
                self.log("Build completed successfully!")
                messagebox.showinfo("Success", "Build completed successfully!")
            else:
                self.log(f"Build failed with return code {process.returncode}")
                messagebox.showerror("Error", "Build failed!")

        except Exception as e:
            self.log(f"An error occurred: {str(e)}")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
        finally:
            self.root.after(0, lambda: self.build_btn.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.install_btn.config(state=tk.NORMAL))

if __name__ == "__main__":
    root = tk.Tk()
    app = PakeGUI(root)
    root.mainloop()
