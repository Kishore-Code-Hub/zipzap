"""ZipZap — Main Window: two-button home screen with Extract & Compress flows."""

import os
import sys
import zipfile

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFileDialog, QMessageBox, QProgressBar,
    QListWidget, QComboBox, QLineEdit, QGroupBox, QFormLayout,
    QStackedWidget, QSizePolicy,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDragEnterEvent, QDropEvent

# Add project root to path for imports
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from ui.themes import STYLE
from core.worker import ExtractWorker, CompressWorker
from utils.helpers import format_size, dir_size


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ZipZap")
        self.setFixedSize(520, 420)
        self.setAcceptDrops(True)
        self.setStyleSheet(STYLE)

        self._worker = None

        # Stacked widget: 0=home, 1=extract, 2=compress
        self._stack = QStackedWidget()
        self.setCentralWidget(self._stack)

        self._stack.addWidget(self._build_home())       # 0
        self._stack.addWidget(self._build_extract())    # 1
        self._stack.addWidget(self._build_compress())   # 2
        self._stack.setCurrentIndex(0)

    # =====================================================================
    # HOME SCREEN
    # =====================================================================
    def _build_home(self) -> QWidget:
        page = QWidget()
        page.setObjectName("home")
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(16)

        title = QLabel("ZipZap")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        sub = QLabel("Fast & simple ZIP utility")
        sub.setObjectName("subtitle")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(sub)

        layout.addSpacing(24)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        btn_row.setAlignment(Qt.AlignmentFlag.AlignCenter)

        btn_extract = QPushButton("📦  Extract")
        btn_extract.setObjectName("bigBtn")
        btn_extract.setFixedSize(180, 90)
        btn_extract.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_extract.clicked.connect(self._start_extract_flow)

        btn_compress = QPushButton("🗜  Compress")
        btn_compress.setObjectName("bigBtn")
        btn_compress.setFixedSize(180, 90)
        btn_compress.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_compress.clicked.connect(self._go_compress)

        # Fix 1: Add buttons to layout only once
        btn_row.addStretch()
        btn_row.addWidget(btn_extract)
        btn_row.addWidget(btn_compress)
        btn_row.addStretch()

        layout.addLayout(btn_row)

        layout.addSpacing(16)
        drop_hint = QLabel("or drag & drop ZIP files here")
        drop_hint.setObjectName("dropHint")
        drop_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(drop_hint)

        return page

    # =====================================================================
    # EXTRACT PAGE
    # =====================================================================
    def _build_extract(self) -> QWidget:
        page = QWidget()
        page.setObjectName("home")
        lay = QVBoxLayout(page)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(12)

        # Header row
        header = QHBoxLayout()
        btn_back = QPushButton("← Back")
        btn_back.setFixedWidth(80)
        btn_back.clicked.connect(lambda: self._stack.setCurrentIndex(0))
        header.addWidget(btn_back)
        lbl = QLabel("Extract ZIP Files")
        lbl.setStyleSheet("font-size:20px; font-weight:bold; color:#e0e0ff;")
        header.addWidget(lbl)
        header.addStretch()
        lay.addLayout(header)

        # File list
        grp = QGroupBox("Selected Archives")
        grp_lay = QVBoxLayout(grp)
        self._ext_list = QListWidget()
        self._ext_list.setMinimumHeight(120)
        grp_lay.addWidget(self._ext_list)

        btn_row = QHBoxLayout()
        btn_add = QPushButton("Add Files…")
        btn_add.clicked.connect(self._ext_add_files)
        
        # Fix 2: Properly clear both the UI list AND the data variables
        btn_clear = QPushButton("Clear")
        btn_clear.clicked.connect(self._ext_clear_files)
        
        btn_row.addWidget(btn_add)
        btn_row.addWidget(btn_clear)
        btn_row.addStretch()
        grp_lay.addLayout(btn_row)
        lay.addWidget(grp)

        # Destination
        dest_row = QHBoxLayout()
        dest_row.addWidget(QLabel("Destination:"))
        self._ext_dest = QLineEdit()
        self._ext_dest.setPlaceholderText("Choose folder…")
        self._ext_dest.setReadOnly(True)
        btn_browse = QPushButton("Browse…")
        btn_browse.clicked.connect(self._ext_browse_dest)
        dest_row.addWidget(self._ext_dest, 1)
        dest_row.addWidget(btn_browse)
        lay.addLayout(dest_row)

        # Progress
        self._ext_progress = QProgressBar()
        self._ext_progress.setValue(0)
        lay.addWidget(self._ext_progress)

        self._ext_status = QLabel("")
        self._ext_status.setStyleSheet("color:#888; font-size:12px;")
        lay.addWidget(self._ext_status)

        # Extract button
        lay.addStretch()
        self._ext_go_btn = QPushButton("⚡  Extract All")
        self._ext_go_btn.setObjectName("primary")
        self._ext_go_btn.setFixedHeight(42)
        self._ext_go_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._ext_go_btn.clicked.connect(self._ext_run)
        lay.addWidget(self._ext_go_btn)

        return page

    def _start_extract_flow(self):
        """Open file picker then go to extract page."""
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select ZIP Files", "", "ZIP Archives (*.zip)"
        )
        if not files:
            return
        self._ext_list.clear()
        self._ext_list.addItems([os.path.basename(f) for f in files])
        self._ext_files = files
        self._ext_dest.setText(os.path.dirname(files[0]))
        self._ext_progress.setValue(0)
        self._ext_status.setText(f"{len(files)} file(s) selected")
        self._stack.setCurrentIndex(1)

    def _ext_add_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select ZIP Files", "", "ZIP Archives (*.zip)"
        )
        if not files:
            return
        if not hasattr(self, '_ext_files'):
            self._ext_files = []
        for f in files:
            if f not in self._ext_files:
                self._ext_files.append(f)
                self._ext_list.addItem(os.path.basename(f))
        self._ext_status.setText(f"{len(self._ext_files)} file(s) selected")
        
    def _ext_clear_files(self):
        """Clears both the UI and underlying data for extract flow."""
        self._ext_list.clear()
        if hasattr(self, '_ext_files'):
            self._ext_files.clear()
        self._ext_status.setText("0 file(s) selected")
        self._ext_progress.setValue(0)

    def _ext_browse_dest(self):
        folder = QFileDialog.getExistingDirectory(self, "Choose Destination")
        if folder:
            self._ext_dest.setText(folder)

    def _ext_run(self):
        if not hasattr(self, '_ext_files') or not self._ext_files:
            QMessageBox.warning(self, "No Files", "Add ZIP files first.")
            return
        dest = self._ext_dest.text().strip()
        if not dest or not os.path.isdir(dest):
            QMessageBox.warning(self, "No Destination", "Choose a destination folder.")
            return
        if self._worker and self._worker.isRunning():
            return

        self._ext_go_btn.setEnabled(False)
        self._ext_progress.setValue(0)

        self._worker = ExtractWorker(list(self._ext_files), dest)
        self._worker.progress.connect(self._ext_progress.setValue)
        self._worker.status.connect(lambda t: self._ext_status.setText(t))
        self._worker.done.connect(self._ext_finished)
        self._worker.start()

    def _ext_finished(self, ok: int, fail: int):
        self._ext_go_btn.setEnabled(True)
        if fail == 0:
            QMessageBox.information(self, "Done ✅", f"All {ok} archive(s) extracted successfully!")
        else:
            QMessageBox.warning(self, "Done", f"{ok} succeeded, {fail} failed.")
        self._ext_status.setText(f"Done — {ok} ok, {fail} failed")

    # =====================================================================
    # COMPRESS PAGE
    # =====================================================================
    def _build_compress(self) -> QWidget:
        page = QWidget()
        page.setObjectName("home")
        lay = QVBoxLayout(page)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(12)

        # Header
        header = QHBoxLayout()
        btn_back = QPushButton("← Back")
        btn_back.setFixedWidth(80)
        btn_back.clicked.connect(lambda: self._stack.setCurrentIndex(0))
        header.addWidget(btn_back)
        lbl = QLabel("Create ZIP Archive")
        lbl.setStyleSheet("font-size:20px; font-weight:bold; color:#e0e0ff;")
        header.addWidget(lbl)
        header.addStretch()
        lay.addLayout(header)

        # Source list
        grp = QGroupBox("Files / Folders to Compress")
        grp_lay = QVBoxLayout(grp)
        self._cmp_list = QListWidget()
        self._cmp_list.setMinimumHeight(100)
        grp_lay.addWidget(self._cmp_list)

        btn_row = QHBoxLayout()
        btn_files = QPushButton("Add Files…")
        btn_files.clicked.connect(self._cmp_add_files)
        btn_folder = QPushButton("Add Folder…")
        btn_folder.clicked.connect(self._cmp_add_folder)
        btn_clear = QPushButton("Clear")
        btn_clear.clicked.connect(self._cmp_clear)
        btn_row.addWidget(btn_files)
        btn_row.addWidget(btn_folder)
        btn_row.addWidget(btn_clear)
        btn_row.addStretch()
        grp_lay.addLayout(btn_row)
        lay.addWidget(grp)

        # Original size
        self._cmp_size_lbl = QLabel("Original size: —")
        self._cmp_size_lbl.setStyleSheet("color:#aaa; font-size:12px;")
        lay.addWidget(self._cmp_size_lbl)

        # Output name
        name_row = QHBoxLayout()
        name_row.addWidget(QLabel("Archive name:"))
        self._cmp_name = QLineEdit()
        self._cmp_name.setPlaceholderText("my_archive.zip")
        name_row.addWidget(self._cmp_name, 1)
        lay.addLayout(name_row)

        #Compression format
        format_row = QHBoxLayout()
        format_row.addWidget(QLabel("Format:"))
        self._cmp_format = QComboBox()
        self._cmp_format.addItems(["ZIP", "7Z"])
        format_row.addWidget(self._cmp_format)
        format_row.addStretch()
        lay.addLayout(format_row)

        # Compression level
        level_row = QHBoxLayout()
        level_row.addWidget(QLabel("Level:"))
        self._cmp_level = QComboBox()
        self._cmp_level.addItems(["Fast", "Normal", "High"])
        self._cmp_level.setCurrentText("Normal")
        level_row.addWidget(self._cmp_level)
        level_row.addStretch()
        lay.addLayout(level_row)

        # Progress
        self._cmp_progress = QProgressBar()
        self._cmp_progress.setValue(0)
        lay.addWidget(self._cmp_progress)

        self._cmp_status = QLabel("")
        self._cmp_status.setStyleSheet("color:#888; font-size:12px;")
        lay.addWidget(self._cmp_status)

        # Result
        self._cmp_result = QLabel("")
        self._cmp_result.setStyleSheet("color:#7c3aed; font-size:13px; font-weight:bold;")
        lay.addWidget(self._cmp_result)

        # Compress button
        lay.addStretch()
        self._cmp_go_btn = QPushButton("⚡  Compress")
        self._cmp_go_btn.setObjectName("primary")
        self._cmp_go_btn.setFixedHeight(42)
        self._cmp_go_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._cmp_go_btn.clicked.connect(self._cmp_run)
        lay.addWidget(self._cmp_go_btn)

        self._cmp_sources: list[str] = []
        self._cmp_total_size = 0

        return page

    def _go_compress(self):
        self._cmp_clear()
        self._stack.setCurrentIndex(2)

    def _cmp_add_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Files")
        for f in files:
            if f not in self._cmp_sources:
                self._cmp_sources.append(f)
                self._cmp_list.addItem(os.path.basename(f))
        self._cmp_update_size()

    def _cmp_add_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder and folder not in self._cmp_sources:
            self._cmp_sources.append(folder)
            self._cmp_list.addItem(f"📁 {os.path.basename(folder)}")
            if not self._cmp_name.text():
                self._cmp_name.setText(os.path.basename(folder) + ".zip")
        self._cmp_update_size()

    def _cmp_clear(self):
        self._cmp_sources.clear()
        self._cmp_list.clear()
        self._cmp_name.clear()
        self._cmp_progress.setValue(0)
        self._cmp_status.clear()
        self._cmp_result.clear()
        self._cmp_total_size = 0
        self._cmp_size_lbl.setText("Original size: —")

    def _cmp_update_size(self):
        total = 0
        for s in self._cmp_sources:
            if os.path.isfile(s):
                total += os.path.getsize(s)
            elif os.path.isdir(s):
                total += dir_size(s)
        self._cmp_total_size = total
        self._cmp_size_lbl.setText(f"Original size: {format_size(total)}")

    def _cmp_run(self):
        if not self._cmp_sources:
            QMessageBox.warning(self, "No Files", "Add files or folders first.")
            return
        name = self._cmp_name.text().strip()
        if not name:
            QMessageBox.warning(self, "No Name", "Enter an archive name.")
            return
        format_selected = self._cmp_format.currentText()

        if format_selected == "ZIP":
            if not name.lower().endswith(".zip"):
                name += ".zip"
        elif format_selected == "7Z":
            if not name.lower().endswith(".7z"):
                name += ".7z"

        dest_dir = QFileDialog.getExistingDirectory(self, "Save archive to…")
        if not dest_dir:
            return

        output = os.path.join(dest_dir, name)
        level_map = {"Fast": 1, "Normal": 6, "High": 9}
        level = level_map.get(self._cmp_level.currentText(), 6)

        if self._worker and self._worker.isRunning():
            return

        self._cmp_go_btn.setEnabled(False)
        self._cmp_progress.setValue(0)
        self._cmp_result.clear()

        self._worker = CompressWorker(list(self._cmp_sources), output, level)
        self._worker.progress.connect(self._cmp_progress.setValue)
        self._worker.status.connect(lambda t: self._cmp_status.setText(t))
        self._worker.done.connect(self._cmp_finished)
        self._worker.start()

    def _cmp_finished(self, ok: bool, msg: str, final_size: int):
        self._cmp_go_btn.setEnabled(True)
        if ok:
            ratio = (1 - final_size / max(self._cmp_total_size, 1)) * 100 if self._cmp_total_size else 0
            self._cmp_result.setText(
                f"✅ Compressed: {format_size(final_size)}  •  "
                f"Saved {ratio:.1f}%"
            )
            self._cmp_status.setText(f"Archive saved to {msg}")
            QMessageBox.information(self, "Done ✅", f"Archive created!\n\nSize: {format_size(final_size)}\nRatio: {ratio:.1f}% saved")
        else:
            QMessageBox.critical(self, "Error", msg)
            self._cmp_status.setText(f"Error: {msg}")

    # =====================================================================
    # DRAG & DROP
    # =====================================================================
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        paths = [u.toLocalFile() for u in event.mimeData().urls()]
        zips = [p for p in paths if p.lower().endswith(".zip")]
        if not zips:
            QMessageBox.information(self, "Not Supported", "Only .zip files are supported.")
            return
        # Go to extract flow with dropped files
        self._ext_list.clear()
        self._ext_files = zips
        self._ext_list.addItems([os.path.basename(f) for f in zips])
        self._ext_dest.setText(os.path.dirname(zips[0]))
        self._ext_progress.setValue(0)
        self._ext_status.setText(f"{len(zips)} file(s) dropped")
        self._stack.setCurrentIndex(1)