# ZipZap

A lightweight, professional archive manager built with Python + PyQt6.
Designed for simplicity, speed, and clean aesthetics — purely utilizing Python's built-in `zipfile` for a standalone, dependency-free experience.

## Features

- **ZIP Format Support**: Fast and reliable ZIP extraction and compression.
- **Dependency-Free**: Pure Python implementation using the built-in `zipfile` module. No external CLI tools like 7-Zip or WinRAR are required.
- **Modern UI**: A clean, intuitive interface featuring a two-button home screen for Extract and Compress flows.
- **Drag & Drop**: Seamlessly drop ZIP files to extract, or drop files and folders to compress them instantly.
- **Smart Extract**: Automatically avoids overwriting existing folders when extracting.
- **Non-blocking Workflows**: Multi-threaded extraction and compression with real-time progress bars and status updates.
- **Stand-alone**: Easily packaged into a single executable.

## Project Structure

```text
d:\zip application\
├── main.py                 # Entry point
├── requirements.txt
├── ui/
│   ├── main_window.py      # Main window (Extract/Compress flows, drag & drop)
│   └── themes.py           # Modern dark UI stylesheet
├── core/
│   ├── archive_manager.py  # Core zipfile extraction / compression logic
│   └── worker.py           # QThread workers for background processing
├── utils/
│   └── helpers.py          # File size formatting utilities
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
pyinstaller --noconfirm --onefile --windowed --name="ZipZap" main.py
```

The output will be in `dist/ZipZap.exe`.
