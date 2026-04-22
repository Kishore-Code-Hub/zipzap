"""Background workers for extract / compress."""

import os
from PyQt6.QtCore import QThread, pyqtSignal
from core.archive_manager import extract_zip, smart_dest, compress_zip


class ExtractWorker(QThread):
    progress = pyqtSignal(int)          # 0-100
    status = pyqtSignal(str)            # current file label
    file_done = pyqtSignal(str, bool, str)  # name, ok, msg
    done = pyqtSignal(int, int)         # ok_count, fail_count

    def __init__(self, archives: list[str], dest: str):
        super().__init__()
        self.archives = archives
        self.dest = dest

    def run(self):
        total = len(self.archives)
        ok = fail = 0
        for idx, arc in enumerate(self.archives):
            name = os.path.basename(arc)
            self.status.emit(f"[{idx+1}/{total}] {name}")
            try:
                out = smart_dest(arc, self.dest)
                os.makedirs(out, exist_ok=True)

                def _cb(cur, tot, fn, _idx=idx):
                    pct = int((_idx + cur / max(tot, 1)) / total * 100)
                    self.progress.emit(min(pct, 99))

                extract_zip(arc, out, _cb)
                self.file_done.emit(name, True, out)
                ok += 1
            except Exception as e:
                self.file_done.emit(name, False, str(e))
                fail += 1

        self.progress.emit(100)
        self.done.emit(ok, fail)


class CompressWorker(QThread):
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    done = pyqtSignal(bool, str, int)  # ok, msg, final_size

    def __init__(self, sources: list[str], output: str, level: int = 6):
        super().__init__()
        self.sources = sources
        self.output = output
        self.level = level

    def run(self):
        try:
            def _cb(cur, tot, fn):
                self.progress.emit(int(cur / max(tot, 1) * 100))
                self.status.emit(fn)

            final_size = compress_zip(self.sources, self.output, self.level, _cb)
            self.progress.emit(100)
            self.done.emit(True, self.output, final_size)
        except Exception as e:
            self.done.emit(False, str(e), 0)
