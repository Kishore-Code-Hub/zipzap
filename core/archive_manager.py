"""Core extraction and compression using zipfile."""

import os
import zipfile
import pathlib


def extract_zip(archive: str, dest: str, progress_cb=None):
    """Extract a single ZIP to *dest*. Calls progress_cb(current, total, name)."""
    with zipfile.ZipFile(archive, "r") as zf:
        members = zf.infolist()
        total = len(members)
        for i, m in enumerate(members):
            zf.extract(m, dest)
            if progress_cb:
                progress_cb(i + 1, total, m.filename)


def smart_dest(archive: str, base_dest: str) -> str:
    """Choose an extraction folder. Avoids overwriting existing folders."""
    stem = pathlib.Path(archive).stem
    dest = os.path.join(base_dest, stem)
    if not os.path.exists(dest):
        return dest
    c = 1
    while os.path.exists(f"{dest} ({c})"):
        c += 1
    return f"{dest} ({c})"


def get_unique_filename(path: str) -> str:
    """Smart auto file naming if file exists."""
    if not os.path.exists(path):
        return path
    directory = os.path.dirname(path)
    filename = os.path.basename(path)
    name, ext = os.path.splitext(filename)
    counter = 1
    while True:
        new_name = f"{name}({counter}){ext}"
        new_path = os.path.join(directory, new_name)
        if not os.path.exists(new_path):
            return new_path
        counter += 1


def compress_zip(sources: list[str], output: str, format: str = "ZIP", level: str = "Normal", progress_cb=None):
    """Compress using pure Python zipfile module."""
    if not output.lower().endswith(".zip"):
        output += ".zip"
        
    output = get_unique_filename(output)

    # Level mapping for zipfile
    level_map = {"Fast": 1, "Normal": 6, "Maximum": 9}
    compresslevel = level_map.get(level, 6)

    # Collect all files to compress to calculate total size or items for progress
    files_to_compress = []
    for src in sources:
        if os.path.isfile(src):
            files_to_compress.append((src, os.path.basename(src)))
        elif os.path.isdir(src):
            base_dir = os.path.dirname(src)
            for root, _, files in os.walk(src):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, base_dir)
                    files_to_compress.append((file_path, arcname))

    total = len(files_to_compress)
    if total == 0:
        raise Exception("No files found to compress.")

    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=compresslevel) as zf:
        for i, (file_path, arcname) in enumerate(files_to_compress):
            zf.write(file_path, arcname)
            if progress_cb:
                pct = int((i + 1) / total * 100)
                progress_cb(pct, arcname)

    return os.path.getsize(output), output

