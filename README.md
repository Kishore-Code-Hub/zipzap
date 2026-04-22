# ZipZap

A lightweight, professional archive manager built with Python + PyQt6.
Works like 7-Zip / WinRAR — fast, clean, and fully open source.

## Features

- **format support**: ZIP
- **File explorer UI**: folder tree (left) + file list (right) with breadcrumb navigation
- **Smart Extract**: auto-detects archive structure; wraps loose files in a folder
- **Compress**: create ZIP archives with Fast / Normal / Ultra compression
- **Drag & Drop**: drop archives or folders directly into the window
- **Dark / Light theme**: toggle instantly via toolbar or menu
- **Context menu**: right-click files for Open, Extract, Delete, Properties
- **Password support**: detects password-protected archives and prompts
- **Progress bar**: real-time feedback during extract/compress
- **Recent files**: remembers last opened archives
- **Keyboard shortcuts**: Ctrl+O, Ctrl+E, Del, Alt+← / Alt+→
- **Logging**: writes to `zipzap.log`

## Project Structure

```
d:\zip application\
├── main.py                 # Entry point
├── requirements.txt
├── ui/
│   ├── main_window.py      # Main window (toolbar, panels, logic)
│   ├── folder_tree.py      # Left panel — folder navigation
│   ├── file_table.py       # Right panel — file list table
│   ├── dialogs.py          # Compress / Password / About dialogs
│   └── themes.py           # Light & Dark QSS stylesheets
├── core/
│   ├── archive_manager.py  # Read / extract / compress logic
│   └── worker.py           # QThread workers
├── utils/
│   ├── helpers.py          # File size formatting, type detection
│   └── settings.py         # QSettings persistence
├── context_menu.reg        # Windows right-click integration
├── create_shortcut.ps1     # Shortcut generator
├── zipzap.jpg              # App icon / logo
└── README.md
```

## Setup

```bash
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

## Build Standalone EXE

```bash
pyinstaller --noconfirm --onefile --windowed --icon="zipzap.ico" --name="ZipZap" main.py
```

The output will be in `dist/ZipZap.exe`.

## Windows Context Menu

Edit paths in `context_menu.reg` to point to your `ZipZap.exe`, then double-click the `.reg` file.

## Create Shortcut

```powershell
powershell -ExecutionPolicy Bypass -File create_shortcut.ps1
```
