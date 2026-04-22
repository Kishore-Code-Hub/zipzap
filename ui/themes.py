"""ZipZap — Minimal theme stylesheet."""

STYLE = """
QMainWindow {
    background: #1a1b2e;
}
QWidget#home {
    background: #1a1b2e;
}
QPushButton#bigBtn {
    background: qlineargradient(x1:0,x2:1, stop:0 #7c3aed, stop:1 #a855f7);
    color: white;
    border: none;
    border-radius: 12px;
    font-size: 18px;
    font-weight: bold;
    padding: 18px 20px;
    min-width: 180px;
    max-width: 200px;
    margin: 0px 10px;
    border: 1px solid rgba(255,255,255,0.1);
}
QPushButton#bigBtn:hover {
    background: qlineargradient(x1:0,x2:1, stop:0 #6d28d9, stop:1 #9333ea);
}
QPushButton#bigBtn:pressed {
    background: #5b21b6;
}
QLabel#title {
    color: #e0e0ff;
    font-size: 32px;
    font-weight: bold;
}
QLabel#subtitle {
    color: #888;
    font-size: 13px;
}
QLabel#dropHint {
    color: #666;
    font-size: 12px;
    padding: 10px;
}
QProgressBar {
    height: 22px;
    border: 1px solid #444;
    border-radius: 6px;
    text-align: center;
    background: #2a2b3e;
    color: #ccc;
    font-size: 12px;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0,x2:1, stop:0 #7c3aed, stop:1 #38bdf8);
    border-radius: 5px;
}
QDialog {
    background: #1e1f33;
    color: #ddd;
}
QLabel {
    color: #ddd;
}
QPushButton {
    background: #3a3b55;
    color: #ddd;
    border: 1px solid #555;
    border-radius: 6px;
    padding: 8px 20px;
    font-size: 13px;
}
QPushButton:hover { background: #4a4b65; }
QPushButton:pressed { background: #7c3aed; }
QPushButton#primary {
    background: #7c3aed;
    border: none;
    color: white;
    font-weight: bold;
}
QPushButton#primary:hover { background: #6d28d9; }
QComboBox, QLineEdit {
    background: #2a2b3e;
    border: 1px solid #555;
    border-radius: 6px;
    padding: 6px 10px;
    color: #ddd;
    font-size: 13px;
}
QComboBox:focus, QLineEdit:focus { border: 1px solid #7c3aed; }
QComboBox QAbstractItemView {
    background: #2a2b3e;
    color: #ddd;
    selection-background-color: #7c3aed;
}
QListWidget {
    background: #22233a;
    border: 1px solid #444;
    border-radius: 8px;
    color: #ccc;
    font-size: 12px;
    padding: 4px;
}
QListWidget::item { padding: 4px 8px; border-radius: 4px; }
QListWidget::item:selected { background: #7c3aed; color: white; }
QGroupBox {
    border: 1px solid #444;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 18px;
    color: #aaa;
    font-size: 12px;
}
QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 6px; }
"""
