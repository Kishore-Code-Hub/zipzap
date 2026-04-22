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


def compress_zip(sources: list[str], output: str, level: int = 6, progress_cb=None):
    """Compress *sources* into a ZIP. Returns final file size."""
    all_files = []
    for s in sources:
        if os.path.isfile(s):
            all_files.append((s, os.path.basename(s)))
        elif os.path.isdir(s):
            base = os.path.dirname(s)
            for root, _, files in os.walk(s):
                for f in files:
                    fp = os.path.join(root, f)
                    all_files.append((fp, os.path.relpath(fp, base)))

    total = len(all_files)
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED, compresslevel=level) as zf:
        for i, (fp, arc) in enumerate(all_files):
            zf.write(fp, arc)
            if progress_cb:
                progress_cb(i + 1, total, arc)

    return os.path.getsize(output)
