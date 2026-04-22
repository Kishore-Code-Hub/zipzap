import os
import zipfile
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

def format_size(size_in_bytes):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_in_bytes < 1024.0:
            return f"{size_in_bytes:.1f} {unit}"
        size_in_bytes /= 1024.0
    return f"{size_in_bytes:.1f} TB"

def get_dir_size(path):
    total = 0
    for dirpath, _, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if not os.path.islink(fp):
                total += os.path.getsize(fp)
    return total

class ZipZapLite:
    def __init__(self, root):
        self.root = root
        self.root.title("ZipZap Lite")
        self.root.geometry("480x420")
        self.root.resizable(False, False)
        
        # Apply a slightly more modern look using ttk
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Main container for our pages
        self.container = tk.Frame(self.root)
        self.container.pack(fill="both", expand=True)

        # Initialize pages
        self.frames = {}
        for F in (HomePage, ExtractPage, CompressPage):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("HomePage")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

# ==========================================
# HOME PAGE
# ==========================================
class HomePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        
        # Center content
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)
        self.grid_columnconfigure(0, weight=1)

        tk.Label(self, text="ZipZap", font=("Helvetica", 24, "bold")).grid(row=1, column=0, pady=(0, 5))
        tk.Label(self, text="Fast & simple ZIP utility (Lite Edition)", fg="gray").grid(row=2, column=0, pady=(0, 30))

        btn_frame = tk.Frame(self)
        btn_frame.grid(row=3, column=0)

        extract_btn = tk.Button(btn_frame, text="📦 Extract", font=("Helvetica", 12, "bold"), 
                                width=15, height=3, bg="#e2e8f0", command=lambda: controller.show_frame("ExtractPage"))
        extract_btn.pack(side="left", padx=10)

        compress_btn = tk.Button(btn_frame, text="🗜 Compress", font=("Helvetica", 12, "bold"), 
                                 width=15, height=3, bg="#e2e8f0", command=lambda: controller.show_frame("CompressPage"))
        compress_btn.pack(side="left", padx=10)


# ==========================================
# EXTRACT PAGE
# ==========================================
class ExtractPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.files_to_extract = []

        # Header
        header = tk.Frame(self)
        header.pack(fill="x", padx=15, pady=15)
        tk.Button(header, text="← Back", command=lambda: controller.show_frame("HomePage")).pack(side="left")
        tk.Label(header, text="Extract ZIP Files", font=("Helvetica", 14, "bold")).pack(side="left", padx=20)

        # File List
        list_frame = tk.LabelFrame(self, text="Selected Archives", padx=10, pady=10)
        list_frame.pack(fill="both", expand=True, padx=15, pady=5)
        
        self.listbox = tk.Listbox(list_frame, height=5)
        self.listbox.pack(fill="both", expand=True)
        
        btn_row = tk.Frame(list_frame)
        btn_row.pack(fill="x", pady=(5,0))
        tk.Button(btn_row, text="Add Files...", command=self.add_files).pack(side="left", padx=(0,5))
        tk.Button(btn_row, text="Clear", command=self.clear_files).pack(side="left")

        # Destination
        dest_frame = tk.Frame(self)
        dest_frame.pack(fill="x", padx=15, pady=10)
        tk.Label(dest_frame, text="Destination:").pack(side="left")
        self.dest_var = tk.StringVar()
        tk.Entry(dest_frame, textvariable=self.dest_var, state="readonly").pack(side="left", fill="x", expand=True, padx=5)
        tk.Button(dest_frame, text="Browse...", command=self.browse_dest).pack(side="left")

        # Progress & Run
        self.progress = ttk.Progressbar(self, orient="horizontal", mode="determinate")
        self.progress.pack(fill="x", padx=15, pady=5)
        
        self.status_lbl = tk.Label(self, text="Ready", fg="gray")
        self.status_lbl.pack(pady=5)

        self.run_btn = tk.Button(self, text="⚡ Extract All", font=("Helvetica", 10, "bold"), 
                                 bg="#4ade80", command=self.start_extraction)
        self.run_btn.pack(fill="x", padx=15, pady=(0, 15), ipady=5)

    def add_files(self):
        files = filedialog.askopenfilenames(filetypes=[("ZIP Archives", "*.zip")])
        for f in files:
            if f not in self.files_to_extract:
                self.files_to_extract.append(f)
                self.listbox.insert(tk.END, os.path.basename(f))
        
        if self.files_to_extract and not self.dest_var.get():
            self.dest_var.set(os.path.dirname(self.files_to_extract[0]))

    def clear_files(self):
        self.files_to_extract.clear()
        self.listbox.delete(0, tk.END)
        self.dest_var.set("")
        self.progress['value'] = 0

    def browse_dest(self):
        folder = filedialog.askdirectory()
        if folder:
            self.dest_var.set(folder)

    def start_extraction(self):
        if not self.files_to_extract:
            messagebox.showwarning("Warning", "Add ZIP files first.")
            return
        if not self.dest_var.get():
            messagebox.showwarning("Warning", "Choose a destination folder.")
            return

        self.run_btn.config(state="disabled")
        self.progress['value'] = 0
        self.status_lbl.config(text="Extracting...")
        
        # Run in a separate thread so the GUI doesn't freeze
        threading.Thread(target=self._extract_worker, daemon=True).start()

    def _extract_worker(self):
        total_files = len(self.files_to_extract)
        success = 0
        
        for idx, zip_path in enumerate(self.files_to_extract):
            try:
                with zipfile.ZipFile(zip_path, 'r') as z:
                    z.extractall(self.dest_var.get())
                success += 1
            except Exception as e:
                print(f"Error extracting {zip_path}: {e}")
            
            # Update progress safely
            progress_pct = ((idx + 1) / total_files) * 100
            self.controller.root.after(0, lambda p=progress_pct: self.progress.configure(value=p))

        self.controller.root.after(0, lambda: self._extraction_done(success, total_files))

    def _extraction_done(self, success, total):
        self.run_btn.config(state="normal")
        self.status_lbl.config(text=f"Done — {success}/{total} successful")
        messagebox.showinfo("Done", f"Extracted {success} out of {total} archives successfully!")


# ==========================================
# COMPRESS PAGE
# ==========================================
class CompressPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.sources = []
        self.total_size = 0

        # Header
        header = tk.Frame(self)
        header.pack(fill="x", padx=15, pady=15)
        tk.Button(header, text="← Back", command=lambda: controller.show_frame("HomePage")).pack(side="left")
        tk.Label(header, text="Create ZIP Archive", font=("Helvetica", 14, "bold")).pack(side="left", padx=20)

        # Source List
        list_frame = tk.LabelFrame(self, text="Files / Folders to Compress", padx=10, pady=10)
        list_frame.pack(fill="both", expand=True, padx=15, pady=5)
        
        self.listbox = tk.Listbox(list_frame, height=4)
        self.listbox.pack(fill="both", expand=True)
        
        btn_row = tk.Frame(list_frame)
        btn_row.pack(fill="x", pady=(5,0))
        tk.Button(btn_row, text="Add Files...", command=self.add_files).pack(side="left", padx=(0,5))
        tk.Button(btn_row, text="Add Folder...", command=self.add_folder).pack(side="left", padx=(0,5))
        tk.Button(btn_row, text="Clear", command=self.clear_files).pack(side="left")

        self.size_lbl = tk.Label(self, text="Original size: —", fg="gray")
        self.size_lbl.pack(anchor="w", padx=15)

        # Output Name
        name_frame = tk.Frame(self)
        name_frame.pack(fill="x", padx=15, pady=10)
        tk.Label(name_frame, text="Archive name:").pack(side="left")
        self.name_var = tk.StringVar()
        tk.Entry(name_frame, textvariable=self.name_var).pack(side="left", fill="x", expand=True, padx=5)

        # Progress & Run
        self.progress = ttk.Progressbar(self, orient="horizontal", mode="determinate")
        self.progress.pack(fill="x", padx=15, pady=5)
        
        self.status_lbl = tk.Label(self, text="Ready", fg="gray")
        self.status_lbl.pack(pady=5)

        self.run_btn = tk.Button(self, text="⚡ Compress", font=("Helvetica", 10, "bold"), 
                                 bg="#60a5fa", command=self.start_compression)
        self.run_btn.pack(fill="x", padx=15, pady=(0, 15), ipady=5)

    def add_files(self):
        files = filedialog.askopenfilenames()
        for f in files:
            if f not in self.sources:
                self.sources.append(f)
                self.listbox.insert(tk.END, os.path.basename(f))
        self.update_size()

    def add_folder(self):
        folder = filedialog.askdirectory()
        if folder and folder not in self.sources:
            self.sources.append(folder)
            self.listbox.insert(tk.END, f"📁 {os.path.basename(folder)}")
            if not self.name_var.get():
                self.name_var.set(os.path.basename(folder) + ".zip")
        self.update_size()

    def clear_files(self):
        self.sources.clear()
        self.listbox.delete(0, tk.END)
        self.name_var.set("")
        self.total_size = 0
        self.size_lbl.config(text="Original size: —")
        self.progress['value'] = 0

    def update_size(self):
        total = 0
        for s in self.sources:
            if os.path.isfile(s):
                total += os.path.getsize(s)
            elif os.path.isdir(s):
                total += get_dir_size(s)
        self.total_size = total
        self.size_lbl.config(text=f"Original size: {format_size(total)}")

    def start_compression(self):
        if not self.sources:
            messagebox.showwarning("Warning", "Add files or folders first.")
            return
        name = self.name_var.get().strip()
        if not name:
            messagebox.showwarning("Warning", "Enter an archive name.")
            return
        if not name.lower().endswith(".zip"):
            name += ".zip"

        dest_dir = filedialog.askdirectory(title="Save archive to...")
        if not dest_dir:
            return

        output_path = os.path.join(dest_dir, name)
        
        self.run_btn.config(state="disabled")
        self.progress['value'] = 0
        self.status_lbl.config(text="Compressing...")

        # Run in a separate thread
        threading.Thread(target=self._compress_worker, args=(output_path,), daemon=True).start()

    def _compress_worker(self, output_path):
        try:
            # First pass: count total files for progress bar
            all_files = []
            for src in self.sources:
                if os.path.isfile(src):
                    all_files.append((src, os.path.basename(src)))
                else:
                    parent_dir = os.path.dirname(src)
                    for root, _, files in os.walk(src):
                        for file in files:
                            full_path = os.path.join(root, file)
                            arcname = os.path.relpath(full_path, parent_dir)
                            all_files.append((full_path, arcname))

            total_files = len(all_files)
            
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                for idx, (filepath, arcname) in enumerate(all_files):
                    zf.write(filepath, arcname)
                    progress_pct = ((idx + 1) / max(total_files, 1)) * 100
                    self.controller.root.after(0, lambda p=progress_pct: self.progress.configure(value=p))

            final_size = os.path.getsize(output_path)
            self.controller.root.after(0, lambda: self._compression_done(True, output_path, final_size))
            
        except Exception as e:
            self.controller.root.after(0, lambda e=e: self._compression_done(False, str(e), 0))

    def _compression_done(self, success, result_msg, final_size):
        self.run_btn.config(state="normal")
        if success:
            ratio = (1 - final_size / max(self.total_size, 1)) * 100 if self.total_size else 0
            self.status_lbl.config(text=f"Archive saved! Size: {format_size(final_size)}")
            messagebox.showinfo("Done", f"Archive created!\n\nSize: {format_size(final_size)}\nSaved: {ratio:.1f}%")
        else:
            self.status_lbl.config(text="Error occurred.")
            messagebox.showerror("Error", f"Failed to compress:\n{result_msg}")


if __name__ == "__main__":
    root = tk.Tk()
    app = ZipZapLite(root)
    root.mainloop()