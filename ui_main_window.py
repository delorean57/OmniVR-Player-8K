"""
OmniVR Player 8K — Interfaz Glassmorphic Completa y Ventana Principal
Inspirado en GoPro VR Player 3.0.5 con aceleración por GPU (NVIDIA RTX / D3D11VA / NVDEC).
Proporciona barra de control inferior flotante, menús nativos completos, HUD OSD y control 360/VR.
"""

import os
import sys
import math
import json
import re
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QSlider, QComboBox, QFileDialog, QFrame,
    QSizePolicy, QToolButton, QMessageBox, QMenu, QMenuBar,
    QInputDialog, QToolTip, QScrollArea, QDialog, QTableWidget,
    QTableWidgetItem, QHeaderView, QLineEdit, QCheckBox,
    QAbstractItemView, QGroupBox, QFormLayout, QDoubleSpinBox,
    QListWidget, QListWidgetItem
)
from PySide6.QtCore import Qt, QTimer, QPoint, QPointF, QSize, Signal, QSettings, QEvent
from PySide6.QtGui import (
    QIcon, QFont, QColor, QPalette, QKeySequence, QShortcut,
    QDragEnterEvent, QDropEvent, QAction, QActionGroup, QCursor, QKeyEvent
)

from vr_engine import VRGLWidget
from player_backend import VRVideoBackend



DARK_STYLESHEET = """
QMainWindow {
    background-color: #080c14;
}

QMenuBar {
    background-color: #0b0f19;
    color: #e2e8f0;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 13px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    padding: 3px 8px;
}

QMenuBar::item {
    background: transparent;
    padding: 4px 10px;
    border-radius: 4px;
}

QMenuBar::item:selected {
    background: rgba(56, 189, 248, 0.2);
    color: #38bdf8;
}

QMenuBar::item:pressed {
    background: rgba(56, 189, 248, 0.35);
}

QMenu {
    background-color: #0f172a;
    color: #f1f5f9;
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 8px;
    padding: 6px;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 12px;
}

QMenu::item {
    padding: 6px 24px 6px 20px;
    border-radius: 4px;
}

QMenu::item:selected {
    background-color: #0284c7;
    color: #ffffff;
}

QMenu::separator {
    height: 1px;
    background: rgba(255, 255, 255, 0.1);
    margin: 4px 8px;
}

/* Floating Bottom Control Bar */
QFrame#bottomControlBar {
    background-color: rgba(13, 20, 32, 0.94);
    border: 1px solid rgba(255, 255, 255, 0.14);
    border-radius: 16px;
}

/* Floating HUD Pill */
QFrame#hudPill {
    background-color: rgba(8, 14, 24, 0.88);
    border: 1px solid rgba(56, 189, 248, 0.38);
    border-radius: 10px;
    padding: 8px 14px;
}

QLabel {
    color: #e2e8f0;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 12px;
}

QLabel#timeLabel {
    color: #94a3b8;
    font-family: 'Consolas', monospace;
    font-size: 12px;
    font-weight: 600;
}

QLabel#badgeLabel {
    background: rgba(56, 189, 248, 0.15);
    border: 1px solid rgba(56, 189, 248, 0.35);
    color: #38bdf8;
    border-radius: 5px;
    padding: 4px 8px;
    font-size: 11px;
    font-weight: bold;
    letter-spacing: 0.5px;
}

/* Base Buttons */
QPushButton, QToolButton {
    background-color: rgba(30, 41, 59, 0.85);
    color: #f8fafc;
    border: 1px solid rgba(255, 255, 255, 0.14);
    border-radius: 6px;
    padding: 4px 8px;
    font-weight: 500;
    font-size: 11px;
    min-height: 28px;
}

QPushButton:hover, QToolButton:hover {
    background-color: rgba(56, 189, 248, 0.25);
    border: 1px solid #38bdf8;
    color: #ffffff;
}

QPushButton:pressed, QToolButton:pressed {
    background-color: rgba(56, 189, 248, 0.45);
}

QPushButton:checked, QToolButton:checked {
    background-color: rgba(2, 132, 199, 0.75);
    border: 1px solid #38bdf8;
    color: #ffffff;
}

/* Square Icon Buttons */
QToolButton#iconBtn {
    min-width: 30px;
    max-width: 32px;
    min-height: 30px;
    max-height: 32px;
    padding: 0px;
    font-size: 13px;
}

/* Dropdown Menu Buttons */
QPushButton#menuBtn, QToolButton#menuBtn {
    padding: 4px 10px;
    font-size: 11px;
}

QPushButton#menuBtn::menu-indicator, QToolButton::menu-indicator {
    width: 0px;
}

/* Circular Glowing Play Button */
QPushButton#playButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #00f2fe, stop:1 #0284c7);
    border: 1px solid #38bdf8;
    border-radius: 19px;
    min-width: 38px;
    max-width: 38px;
    min-height: 38px;
    max-height: 38px;
    font-size: 16px;
    color: #ffffff;
    font-weight: bold;
    padding: 0px;
}

QPushButton#playButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #38bdf8, stop:1 #0369a1);
    border: 1px solid #ffffff;
}

/* Interactive Timeline Seek Slider */
QSlider#seekSlider::groove:horizontal {
    height: 6px;
    background: rgba(51, 65, 85, 0.7);
    border-radius: 3px;
}

QSlider#seekSlider::sub-page:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0284c7, stop:1 #38bdf8);
    border-radius: 3px;
}

QSlider#seekSlider::handle:horizontal {
    background: #ffffff;
    border: 2px solid #0284c7;
    width: 14px;
    margin-top: -4px;
    margin-bottom: -4px;
    border-radius: 7px;
}

QSlider#seekSlider::handle:horizontal:hover {
    background: #38bdf8;
    border: 2px solid #ffffff;
    width: 16px;
    margin-top: -5px;
    margin-bottom: -5px;
    border-radius: 8px;
}

/* Volume Slider */
QSlider#volSlider::groove:horizontal {
    height: 4px;
    background: rgba(51, 65, 85, 0.7);
    border-radius: 2px;
}

QSlider#volSlider::sub-page:horizontal {
    background: #38bdf8;
    border-radius: 2px;
}

QSlider#volSlider::handle:horizontal {
    background: #ffffff;
    border: 1px solid #38bdf8;
    width: 10px;
    margin-top: -3px;
    margin-bottom: -3px;
    border-radius: 5px;
}

/* Welcome Card */
QFrame#welcomeCard {
    background-color: rgba(13, 20, 32, 0.94);
    border: 1px solid rgba(56, 189, 248, 0.35);
    border-radius: 20px;
    padding: 28px;
}

/* In-Viewport Glassmorphic Overlay Menu */
QFrame#vrOverlayMenu {
    background-color: rgba(13, 20, 32, 0.96);
    border: 1px solid rgba(56, 189, 248, 0.45);
    border-radius: 12px;
}

QPushButton#overlayItem {
    background-color: transparent;
    color: #e2e8f0;
    text-align: left;
    padding: 7px 16px;
    border: none;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 500;
    min-height: 20px;
}

QPushButton#overlayItem:hover {
    background-color: #0284c7;
    color: #ffffff;
}

QPushButton#overlayItem:pressed {
    background-color: #0369a1;
}

QPushButton#overlayHeader {
    background-color: rgba(56, 189, 248, 0.12);
    color: #38bdf8;
    text-align: left;
    padding: 6px 14px;
    border-radius: 6px;
    font-size: 11px;
    font-weight: bold;
    border: 1px solid rgba(56, 189, 248, 0.25);
    min-height: 20px;
}

QPushButton#overlayHeader:hover {
    background-color: rgba(56, 189, 248, 0.25);
}

QLabel#overlayTitle {
    color: #38bdf8;
    font-size: 12px;
    font-weight: bold;
    padding: 5px 12px 3px 12px;
}

QFrame#overlaySeparator {
    background-color: rgba(255, 255, 255, 0.12);
    max-height: 1px;
    min-height: 1px;
    margin: 4px 6px;
}

QFrame#vrOverlayMenu QScrollBar:vertical {
    border: none;
    background: rgba(15, 23, 42, 0.6);
    width: 6px;
    margin: 4px 2px 4px 0px;
    border-radius: 3px;
}

QFrame#vrOverlayMenu QScrollBar::handle:vertical {
    background: #38bdf8;
    min-height: 20px;
    border-radius: 3px;
}

QFrame#vrOverlayMenu QScrollBar::add-line:vertical, QFrame#vrOverlayMenu QScrollBar::sub-line:vertical {
    height: 0px;
}

/* In-Viewport ToolTip (100% visible en pantalla completa con GPU) */
QFrame#inViewportToolTip {
    background-color: rgba(13, 20, 32, 0.96);
    border: 1px solid #38bdf8;
    border-radius: 6px;
}

QLabel#inViewportToolTipText {
    color: #f8fafc;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 11px;
    font-weight: 600;
}

/* Dialogs, Message Boxes & Custom Popups (Alto contraste Glassmorphic) */
QDialog, QMessageBox, QInputDialog {
    background-color: #0b1120;
    color: #f1f5f9;
    border: 1px solid rgba(56, 189, 248, 0.4);
    border-radius: 12px;
}

QDialog QLabel, QMessageBox QLabel, QInputDialog QLabel {
    color: #e2e8f0;
    font-family: 'Segoe UI', Arial, sans-serif;
}

QDialog QPushButton, QMessageBox QPushButton, QInputDialog QPushButton {
    background-color: rgba(30, 41, 59, 0.85);
    color: #f8fafc;
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 6px;
    padding: 6px 16px;
    font-weight: 500;
    font-size: 12px;
}

QDialog QPushButton:hover, QMessageBox QPushButton:hover, QInputDialog QPushButton:hover {
    background-color: rgba(56, 189, 248, 0.25);
    border: 1px solid #38bdf8;
    color: #ffffff;
}

QPushButton#primaryBtn, QPushButton#closeBtn {
    background-color: #0284c7;
    border: 1px solid #38bdf8;
    color: #ffffff;
    font-weight: bold;
    border-radius: 6px;
    padding: 7px 22px;
    font-size: 12px;
}

QPushButton#primaryBtn:hover, QPushButton#closeBtn:hover {
    background-color: #38bdf8;
    color: #080c14;
}

QLineEdit, QSpinBox, QDoubleSpinBox {
    background-color: #0f172a;
    border: 1px solid rgba(56, 189, 248, 0.3);
    color: #f8fafc;
    border-radius: 6px;
    padding: 6px 10px;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 12px;
}

QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {
    border: 1px solid #38bdf8;
    background-color: #1e293b;
}

QComboBox {
    background-color: #0f172a;
    border: 1px solid rgba(56, 189, 248, 0.3);
    color: #f8fafc;
    border-radius: 6px;
    padding: 6px 10px;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 12px;
}

QComboBox:focus, QComboBox:hover {
    border: 1px solid #38bdf8;
    background-color: #1e293b;
}

QComboBox::drop-down {
    border: none;
    padding-right: 8px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid #38bdf8;
    margin-right: 6px;
}

QComboBox QAbstractItemView {
    background-color: #0f172a;
    color: #f1f5f9;
    selection-background-color: #0284c7;
    border: 1px solid #38bdf8;
}

QCheckBox, QRadioButton {
    color: #f1f5f9;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 12px;
    spacing: 8px;
}

QCheckBox:hover, QRadioButton:hover {
    color: #38bdf8;
}

QDialog QCheckBox, QMessageBox QCheckBox, QInputDialog QCheckBox {
    color: #f1f5f9;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 12px;
}

QTableWidget {
    background-color: #080d1a;
    color: #f1f5f9;
    gridline-color: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(56, 189, 248, 0.25);
    border-radius: 8px;
    font-size: 12px;
    selection-background-color: rgba(2, 132, 199, 0.6);
}

QHeaderView::section {
    background-color: #0f172a;
    color: #38bdf8;
    font-weight: bold;
    padding: 6px;
    border: 1px solid rgba(255, 255, 255, 0.05);
}

QGroupBox {
    color: #38bdf8;
    font-weight: bold;
    border: 1px solid rgba(56, 189, 248, 0.25);
    border-radius: 8px;
    margin-top: 14px;
    padding-top: 14px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px;
    padding: 0 4px;
}

QScrollBar:vertical {
    background: #080d1a;
    width: 8px;
    margin: 0px;
    border-radius: 4px;
}

QScrollBar::handle:vertical {
    background: rgba(56, 189, 248, 0.35);
    min-height: 20px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background: #38bdf8;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
"""


# -----------------------------------------------------------------------------
# Reglas Predeterminadas y Administrador de Patrones de Nombre de Archivo
# -----------------------------------------------------------------------------
DEFAULT_FILENAME_PATTERNS = [
    {
        "id": "vr190_fisheye",
        "name": "VR 190° Fisheye SBS (Canon RF 5.2mm / Gran Domo)",
        "pattern": r"fisheye190|190.*fisheye|190_3dh|190.*sbs|vr190|rf5\.2|canon.*190",
        "stereo": "VR180_SBS",
        "dome_fov": 190.0,
        "lens_model": 1,
        "projection": "RECTILINEAR",
        "enabled": True
    },
    {
        "id": "vr180_sbs",
        "name": "VR 180° SBS (3dh / LR / Half-SBS / 180x180)",
        "pattern": r"180x180_3dh|180.*3dh|3dh.*180|lr.*180|180.*lr|180.*sbs|sbs.*180|vr180|180x180",
        "stereo": "VR180_SBS",
        "dome_fov": 180.0,
        "lens_model": 0,
        "projection": "RECTILINEAR",
        "enabled": True
    },
    {
        "id": "vr180_ou",
        "name": "VR 180° Over-Under (3dv / TB / OU)",
        "pattern": r"180x180_3dv|180.*3dv|3dv.*180|tb.*180|180.*tb|ou.*180|180.*ou",
        "stereo": "360_OU",
        "dome_fov": 180.0,
        "lens_model": 0,
        "projection": "RECTILINEAR",
        "enabled": True
    },
    {
        "id": "360_sbs",
        "name": "360° SBS (3D Horizontal / Left-Right)",
        "pattern": r"360.*3dh|3dh.*360|360.*sbs|sbs.*360|360.*lr|lr.*360|360x180.*3dh",
        "stereo": "360_SBS",
        "dome_fov": 180.0,
        "lens_model": 0,
        "projection": "RECTILINEAR",
        "enabled": True
    },
    {
        "id": "360_ou",
        "name": "360° Over-Under (3D Vertical / Top-Bottom)",
        "pattern": r"360.*3dv|3dv.*360|360.*tb|tb.*360|360.*ou|ou.*360|overunder|topbottom",
        "stereo": "360_OU",
        "dome_fov": 180.0,
        "lens_model": 0,
        "projection": "RECTILINEAR",
        "enabled": True
    },
    {
        "id": "360_mono",
        "name": "VR 360° Esférico Monoscópico 2D",
        "pattern": r"360|pano|equirectangular|sphere",
        "stereo": "MONO",
        "dome_fov": 180.0,
        "lens_model": 0,
        "projection": "RECTILINEAR",
        "enabled": True
    }
]


class VRFilenamePatternManager:
    """Administra las reglas de auto-detección por patrones en nombres de archivo con persistencia en QSettings."""
    def __init__(self, settings: QSettings = None):
        self.settings = settings or QSettings("OmniVR", "OmniVRPlayer")
        self.rules = self.load_rules()

    def load_rules(self):
        saved = self.settings.value("filename_pattern_rules", None)
        if saved:
            try:
                data = json.loads(saved)
                if isinstance(data, list) and len(data) > 0:
                    return data
            except Exception as e:
                print(f"[PatternManager] Error al cargar reglas guardadas: {e}")
        return [dict(r) for r in DEFAULT_FILENAME_PATTERNS]

    def save_rules(self, rules):
        self.rules = rules
        try:
            self.settings.setValue("filename_pattern_rules", json.dumps(rules, ensure_ascii=False, indent=2))
            self.settings.sync()
        except Exception as e:
            print(f"[PatternManager] Error al guardar reglas: {e}")

    def reset_to_defaults(self):
        self.rules = [dict(r) for r in DEFAULT_FILENAME_PATTERNS]
        self.save_rules(self.rules)
        return self.rules

    def match(self, filename: str):
        lower = filename.lower()
        for rule in self.rules:
            if not rule.get("enabled", True):
                continue
            pat = rule.get("pattern", "")
            if not pat:
                continue
            try:
                if re.search(pat, lower, re.IGNORECASE):
                    return rule
            except Exception as e:
                print(f"[PatternManager] Error de expresión regular en '{rule.get('name')}': {e}")
        return None


# -----------------------------------------------------------------------------
# Diálogos Glassmorphic Modernos (Atajos, Acerca de, Configuración de Patrones)
# -----------------------------------------------------------------------------
class VREditPatternRuleDialog(QDialog):
    """Diálogo modal para crear o editar una regla de reconocimiento por nombre de archivo."""
    def __init__(self, rule_data=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configurar Regla de Nombre de Archivo")
        self.resize(520, 420)
        self.setStyleSheet(DARK_STYLESHEET)

        self.rule_data = dict(rule_data) if rule_data else {
            "name": "Nueva Regla",
            "pattern": "",
            "stereo": "VR180_SBS",
            "dome_fov": 180.0,
            "lens_model": 0,
            "projection": "RECTILINEAR",
            "enabled": True
        }

        layout = QVBoxLayout(self)
        layout.setSpacing(14)

        title = QLabel("🏷️ Configuración de Regla de Auto-Detección")
        title.setStyleSheet("font-size: 15px; font-weight: bold; color: #38bdf8;")
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(10)

        self.in_name = QLineEdit(self.rule_data.get("name", ""))
        self.in_name.setPlaceholderText("Ej. VR 190° Fisheye SBS")
        form.addRow("Nombre de Regla:", self.in_name)

        self.in_pattern = QLineEdit(self.rule_data.get("pattern", ""))
        self.in_pattern.setPlaceholderText("Ej. fisheye190|190.*3dh|8k_fisheye")
        form.addRow("Patrón (Palabras o Regex):", self.in_pattern)

        help_lbl = QLabel("<span style='color:#94a3b8; font-size:11px;'>Separe palabras clave con <b>|</b> (ej: <i>180_3dh|lr_180</i>). No distingue mayúsculas.</span>")
        form.addRow("", help_lbl)

        self.cb_stereo = QComboBox()
        self.cb_stereo.addItem("2D Mono (Estándar)", "MONO")
        self.cb_stereo.addItem("🕶️ VR 180° SBS (Side-by-Side)", "VR180_SBS")
        self.cb_stereo.addItem("🕶️ VR 190° SBS (Canon RF 5.2mm)", "VR190_SBS")
        self.cb_stereo.addItem("🕶️ 360° SBS", "360_SBS")
        self.cb_stereo.addItem("🕶️ 360° Over-Under (Top-Bottom)", "360_OU")
        self.cb_stereo.addItem("👁️ VR 180° SBS (Ojo Derecho)", "VR180_SBS_RIGHT")
        self.cb_stereo.addItem("👁️ VR 190° SBS (Ojo Derecho)", "VR190_SBS_RIGHT")
        cur_s = self.rule_data.get("stereo", "VR180_SBS")
        idx_s = self.cb_stereo.findData(cur_s)
        if idx_s >= 0:
            self.cb_stereo.setCurrentIndex(idx_s)
        form.addRow("Modo Estéreo 3D:", self.cb_stereo)

        self.spin_dome = QDoubleSpinBox()
        self.spin_dome.setRange(90.0, 360.0)
        self.spin_dome.setSingleStep(5.0)
        self.spin_dome.setDecimals(1)
        self.spin_dome.setSuffix("°")
        self.spin_dome.setValue(float(self.rule_data.get("dome_fov", 180.0)))
        form.addRow("Cobertura Domo (FOV):", self.spin_dome)

        self.cb_lens = QComboBox()
        self.cb_lens.addItem("Equirrectangular Estándar (Domo 180°/360°)", 0)
        self.cb_lens.addItem("Ojo de Pez Circular (Canon RF 5.2mm / Dual Fisheye)", 1)
        cur_lens = int(self.rule_data.get("lens_model", 0))
        idx_lens = self.cb_lens.findData(cur_lens)
        if idx_lens >= 0:
            self.cb_lens.setCurrentIndex(idx_lens)
        form.addRow("Modelo de Lente:", self.cb_lens)

        self.cb_proj = QComboBox()
        self.cb_proj.addItem("📷 Rectilíneo (GoPro VR estándar)", "RECTILINEAR")
        self.cb_proj.addItem("🪐 Little Planet (Pequeño Planeta)", "LITTLE_PLANET")
        self.cb_proj.addItem("🐟 Ojo de Pez (Fisheye)", "FISHEYE")
        self.cb_proj.addItem("🏛️ Panini (Cilíndrico Panorámico)", "PANINI")
        self.cb_proj.addItem("🌐 Esférico 360° (Equirectangular Plano)", "SPHERICAL_360")
        self.cb_proj.addItem("(No alterar proyección actual)", "KEEP")
        cur_proj = self.rule_data.get("projection", "RECTILINEAR")
        idx_proj = self.cb_proj.findData(cur_proj)
        if idx_proj >= 0:
            self.cb_proj.setCurrentIndex(idx_proj)
        form.addRow("Proyección de Cámara:", self.cb_proj)

        self.chk_enabled = QCheckBox("Habilitar esta regla")
        self.chk_enabled.setChecked(self.rule_data.get("enabled", True))
        self.chk_enabled.setStyleSheet("color: #f1f5f9; font-size: 12px; font-weight: 500;")
        form.addRow("", self.chk_enabled)

        layout.addLayout(form)

        btns = QHBoxLayout()
        btns.addStretch()
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.clicked.connect(self.reject)
        btns.addWidget(btn_cancel)

        btn_ok = QPushButton("Aceptar")
        btn_ok.setObjectName("primaryBtn")
        btn_ok.clicked.connect(self._on_accept)
        btns.addWidget(btn_ok)

        layout.addLayout(btns)
        self.cb_stereo.currentIndexChanged.connect(self._on_stereo_changed)

    def _on_stereo_changed(self):
        s_data = self.cb_stereo.currentData()
        if s_data in ["VR190_SBS", "VR190_SBS_RIGHT"]:
            self.spin_dome.setValue(190.0)
            self.cb_lens.setCurrentIndex(self.cb_lens.findData(1))
        elif s_data in ["VR180_SBS", "VR180_SBS_RIGHT"]:
            self.spin_dome.setValue(180.0)
            self.cb_lens.setCurrentIndex(self.cb_lens.findData(0))

    def _on_accept(self):
        name = self.in_name.text().strip()
        pattern = self.in_pattern.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "Debe ingresar un nombre para la regla.")
            return
        if not pattern:
            QMessageBox.warning(self, "Error", "Debe ingresar al menos un patrón de búsqueda.")
            return

        try:
            re.compile(pattern)
        except Exception as e:
            QMessageBox.warning(self, "Patrón Inválido", f"El patrón ingresado no es válido:\n{e}")
            return

        stereo_val = self.cb_stereo.currentData()
        if stereo_val == "VR190_SBS":
            stereo_val = "VR180_SBS"
            dome_fov = 190.0
            lens_model = 1
        else:
            dome_fov = self.spin_dome.value()
            lens_model = self.cb_lens.currentData()

        self.rule_data["name"] = name
        self.rule_data["pattern"] = pattern
        self.rule_data["stereo"] = stereo_val
        self.rule_data["dome_fov"] = dome_fov
        self.rule_data["lens_model"] = lens_model
        self.rule_data["projection"] = self.cb_proj.currentData()
        self.rule_data["enabled"] = self.chk_enabled.isChecked()

        self.accept()

    def get_rule_data(self):
        return self.rule_data


class VRFilenamePatternsDialog(QDialog):
    """Diálogo de gestión completa de patrones de nombre de archivo con probador en vivo."""
    def __init__(self, pattern_manager: VRFilenamePatternManager, sample_filename: str = "", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configurar Patrones de Nombre de Archivo")
        self.resize(840, 560)
        self.setStyleSheet(DARK_STYLESHEET)
        self.pattern_manager = pattern_manager
        self.rules = [dict(r) for r in self.pattern_manager.rules]

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        header = QLabel("🏷️ PATRONES DE AUTO-DETECCIÓN POR NOMBRE DE ARCHIVO")
        header.setStyleSheet("font-size: 16px; font-weight: bold; color: #38bdf8;")
        sub = QLabel("Configure cómo OmniVR Player selecciona automáticamente la proyección, ángulo de cúpula y estéreo según el nombre del video.")
        sub.setStyleSheet("color: #94a3b8; font-size: 12px; margin-bottom: 4px;")
        layout.addWidget(header)
        layout.addWidget(sub)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Activo", "Nombre de Regla", "Patrón de Búsqueda", "Modo Estéreo", "Domo FOV", "Lente"
        ])
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Interactive)
        self.table.setColumnWidth(1, 210)
        self.table.setColumnWidth(3, 110)
        self.table.setColumnWidth(5, 120)
        layout.addWidget(self.table)

        tbl_btns = QHBoxLayout()
        btn_add = QPushButton("➕ Añadir Regla")
        btn_add.clicked.connect(self._add_rule)
        tbl_btns.addWidget(btn_add)

        btn_edit = QPushButton("✏️ Editar")
        btn_edit.clicked.connect(self._edit_selected_rule)
        tbl_btns.addWidget(btn_edit)

        btn_del = QPushButton("🗑️ Eliminar")
        btn_del.clicked.connect(self._delete_selected_rule)
        tbl_btns.addWidget(btn_del)

        btn_up = QPushButton("🔼 Subir")
        btn_up.clicked.connect(self._move_up)
        tbl_btns.addWidget(btn_up)

        btn_down = QPushButton("🔽 Bajar")
        btn_down.clicked.connect(self._move_down)
        tbl_btns.addWidget(btn_down)

        tbl_btns.addStretch()

        btn_reset = QPushButton("🔄 Predeterminados")
        btn_reset.clicked.connect(self._reset_defaults)
        tbl_btns.addWidget(btn_reset)

        layout.addLayout(tbl_btns)

        test_grp = QGroupBox("🧪 Probador en Vivo de Coincidencia de Nombres")
        test_layout = QVBoxLayout(test_grp)
        test_row = QHBoxLayout()
        test_lbl = QLabel("Nombre de archivo a probar:")
        test_lbl.setStyleSheet("font-weight: 500;")
        self.in_test = QLineEdit(sample_filename or "8K_FISHEYE190.mp4")
        self.in_test.setPlaceholderText("Ej. 8K_FISHEYE190.mp4, 180x180_3dh.mp4, 8K_LR_180.mp4...")
        self.in_test.textChanged.connect(self._run_live_test)
        test_row.addWidget(test_lbl)
        test_row.addWidget(self.in_test)
        test_layout.addLayout(test_row)

        self.lbl_test_result = QLabel("")
        self.lbl_test_result.setStyleSheet("padding: 4px 6px; font-weight: bold; border-radius: 4px;")
        test_layout.addWidget(self.lbl_test_result)
        layout.addWidget(test_grp)

        bottom_btns = QHBoxLayout()
        bottom_btns.addStretch()
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.clicked.connect(self.reject)
        bottom_btns.addWidget(btn_cancel)

        btn_save = QPushButton("Guardar Cambios")
        btn_save.setObjectName("primaryBtn")
        btn_save.clicked.connect(self._save_and_close)
        bottom_btns.addWidget(btn_save)

        layout.addLayout(bottom_btns)

        self._refresh_table()
        self._run_live_test()

    def _refresh_table(self):
        self.table.setRowCount(len(self.rules))
        for row, rule in enumerate(self.rules):
            chk = QCheckBox()
            chk.setChecked(rule.get("enabled", True))
            chk.toggled.connect(lambda val, r=row: self._on_rule_toggled(r, val))
            chk_widget = QWidget()
            chk_l = QHBoxLayout(chk_widget)
            chk_l.addWidget(chk)
            chk_l.setAlignment(Qt.AlignCenter)
            chk_l.setContentsMargins(0, 0, 0, 0)
            self.table.setCellWidget(row, 0, chk_widget)

            self.table.setItem(row, 1, QTableWidgetItem(rule.get("name", "")))
            self.table.setItem(row, 2, QTableWidgetItem(rule.get("pattern", "")))
            st_text = rule.get("stereo", "MONO")
            if st_text == "VR180_SBS":
                st_disp = "VR180 SBS" if rule.get("dome_fov", 180) != 190 else "VR190 SBS"
            elif st_text == "360_SBS":
                st_disp = "360° SBS"
            elif st_text == "360_OU":
                st_disp = "360° Over-Under"
            else:
                st_disp = "2D Mono"
            self.table.setItem(row, 3, QTableWidgetItem(st_disp))
            self.table.setItem(row, 4, QTableWidgetItem(f"{rule.get('dome_fov', 180.0):.0f}°"))
            lens_txt = "Ojo de Pez (Fisheye)" if rule.get("lens_model", 0) == 1 else "Equirrectangular"
            self.table.setItem(row, 5, QTableWidgetItem(lens_txt))

    def _on_rule_toggled(self, row, val):
        if 0 <= row < len(self.rules):
            self.rules[row]["enabled"] = val
            self._run_live_test()

    def _add_rule(self):
        dlg = VREditPatternRuleDialog(parent=self)
        if dlg.exec() == QDialog.Accepted:
            self.rules.append(dlg.get_rule_data())
            self._refresh_table()
            self._run_live_test()

    def _edit_selected_rule(self):
        cur_row = self.table.currentRow()
        if cur_row < 0 or cur_row >= len(self.rules):
            QMessageBox.information(self, "Seleccionar Regla", "Por favor seleccione una regla de la tabla para editar.")
            return
        dlg = VREditPatternRuleDialog(self.rules[cur_row], parent=self)
        if dlg.exec() == QDialog.Accepted:
            self.rules[cur_row] = dlg.get_rule_data()
            self._refresh_table()
            self._run_live_test()

    def _delete_selected_rule(self):
        cur_row = self.table.currentRow()
        if cur_row < 0 or cur_row >= len(self.rules):
            return
        r_name = self.rules[cur_row].get("name", "esta regla")
        ret = QMessageBox.question(self, "Eliminar Regla", f"¿Desea eliminar la regla '{r_name}'?", QMessageBox.Yes | QMessageBox.No)
        if ret == QMessageBox.Yes:
            self.rules.pop(cur_row)
            self._refresh_table()
            self._run_live_test()

    def _move_up(self):
        cur = self.table.currentRow()
        if cur > 0:
            self.rules[cur], self.rules[cur - 1] = self.rules[cur - 1], self.rules[cur]
            self._refresh_table()
            self.table.selectRow(cur - 1)
            self._run_live_test()

    def _move_down(self):
        cur = self.table.currentRow()
        if 0 <= cur < len(self.rules) - 1:
            self.rules[cur], self.rules[cur + 1] = self.rules[cur + 1], self.rules[cur]
            self._refresh_table()
            self.table.selectRow(cur + 1)
            self._run_live_test()

    def _reset_defaults(self):
        ret = QMessageBox.question(self, "Restablecer Predeterminados", "¿Desea restablecer todas las reglas de detección a los valores originales de fábrica?", QMessageBox.Yes | QMessageBox.No)
        if ret == QMessageBox.Yes:
            self.rules = [dict(r) for r in DEFAULT_FILENAME_PATTERNS]
            self._refresh_table()
            self._run_live_test()

    def _run_live_test(self):
        filename = self.in_test.text().strip().lower()
        if not filename:
            self.lbl_test_result.setText("<span style='color:#94a3b8;'>Escriba un nombre de archivo para verificar coincidencia.</span>")
            return
        matched = None
        for r in self.rules:
            if not r.get("enabled", True):
                continue
            pat = r.get("pattern", "")
            if not pat:
                continue
            try:
                if re.search(pat, filename, re.IGNORECASE):
                    matched = r
                    break
            except Exception:
                pass

        if matched:
            st = matched.get("stereo", "MONO")
            dome = matched.get("dome_fov", 180.0)
            lens = "Ojo de Pez Circular (Canon RF 5.2mm)" if matched.get("lens_model", 0) == 1 else "Equirrectangular Estándar"
            self.lbl_test_result.setText(
                f"<span style='color:#38bdf8;'>✔ COINCIDENCIA:</span> Regla <b>'{matched['name']}'</b> &nbsp;→&nbsp; "
                f"<span style='color:#4ade80;'>Estéreo: {st} | Domo: {dome:.0f}° | Lente: {lens}</span>"
            )
            self.lbl_test_result.setStyleSheet("background: rgba(34, 197, 94, 0.12); border: 1px solid rgba(34, 197, 94, 0.3); border-radius: 6px; padding: 6px;")
        else:
            self.lbl_test_result.setText(
                "<span style='color:#f87171;'>✖ NINGUNA COINCIDENCIA:</span> Se aplicará el modo predeterminado <b>2D Mono (360° Estándar)</b>."
            )
            self.lbl_test_result.setStyleSheet("background: rgba(239, 68, 68, 0.12); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 6px; padding: 6px;")

    def _save_and_close(self):
        self.pattern_manager.save_rules(self.rules)
        self.accept()


DEFAULT_TOOLBAR_ORDER = [
    "btn_open",
    "btn_prev5",
    "btn_play",
    "btn_next5",
    "btn_stop",
    "volume_group",
    "btn_proj_menu",
    "btn_stereo_menu",
    "btn_speed_menu",
    "btn_fov",
    "spacer",
    "btn_loop",
    "btn_recenter",
    "btn_toggle_eye",
    "btn_orbit",
    "btn_invert_axes",
    "btn_hud_btn",
    "btn_flip_x_btn",
    "btn_flip_btn",
    "btn_fullscreen",
    "badge_label",
]

DEFAULT_TOOLBAR_VISIBILITY = {
    "btn_open": True,
    "btn_prev5": True,
    "btn_play": True,
    "btn_next5": True,
    "btn_stop": True,
    "volume_group": True,
    "btn_proj_menu": True,
    "btn_stereo_menu": True,
    "btn_speed_menu": True,
    "btn_fov": True,
    "spacer": True,
    "btn_loop": True,
    "btn_recenter": True,
    "btn_toggle_eye": True,    # Activado por defecto en la barra
    "btn_orbit": False,        # Sustituido por el botón de alternar ojo por defecto
    "btn_invert_axes": True,
    "btn_hud_btn": True,
    "btn_flip_x_btn": True,
    "btn_flip_btn": True,
    "btn_fullscreen": True,
    "badge_label": True,
}

TOOLBAR_ITEM_LABELS = {
    "btn_open": "📁 Abrir archivo de video (Ctrl+O)",
    "btn_prev5": "⏪ Retroceder 5 segundos",
    "btn_play": "▶ / ⏸ Reproducir y pausar (Espacio)",
    "btn_next5": "⏩ Adelantar 5 segundos",
    "btn_stop": "⏹ Detener y reiniciar al inicio (Home)",
    "volume_group": "🔊 Control y barra de volumen",
    "btn_proj_menu": "📷 Menú de proyecciones 360 / VR",
    "btn_stereo_menu": "🕶️ Menú de modo 3D estéreo (VR180 / 190 / 360)",
    "btn_speed_menu": "⚡ Menú de velocidad de reproducción",
    "btn_fov": "🔍 Menú y selector de FOV / Zoom",
    "spacer": "↔ Espaciador flexible (Separador Izq / Der)",
    "btn_loop": "🔁 Repetición en bucle (Ctrl+L)",
    "btn_recenter": "🎯 Centrar cámara al frente (R)",
    "btn_toggle_eye": "👁️ Alternar Ojo Izquierdo ⇄ Derecho (E)",
    "btn_orbit": "🔄 Giro automático 360° (Auto-Orbit)",
    "btn_invert_axes": "🔀 Menú de inversión de ejes (I)",
    "btn_hud_btn": "ℹ️ HUD / Telemetría OSD en pantalla (H)",
    "btn_flip_x_btn": "⇄ Invertir orientación horizontal (Espejo)",
    "btn_flip_btn": "⇅ Invertir orientación vertical",
    "btn_fullscreen": "⛶ Alternar pantalla completa (F / F11)",
    "badge_label": "⚡ Insignia GPU 8K NVDEC",
}


class VRCustomizeToolbarDialog(QDialog):
    """
    Diálogo Glassmorphic de Personalización y Reordenación de la Barra de Controles Inferior.
    Permite activar, ocultar y reordenar cualquier botón mediante arrastrar y soltar (Drag & Drop)
    o utilizando los botones Subir / Bajar.
    """
    def __init__(self, main_window, parent=None):
        super().__init__(parent or main_window)
        self.main_window = main_window
        self.setWindowTitle("Personalizar y Reordenar Barra de Controles")
        self.resize(580, 660)
        self.setStyleSheet(DARK_STYLESHEET)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        header = QLabel("⚙️ PERSONALIZAR Y REORDENAR BARRA DE CONTROLES")
        header.setStyleSheet("font-size: 16px; font-weight: bold; color: #38bdf8;")
        sub = QLabel(
            "• Active o desactive las casillas para mostrar u ocultar botones.<br>"
            "• <b>Arrastre los elementos</b> con el ratón o use los botones <b>▲ / ▼</b> para cambiar su posición en la barra."
        )
        sub.setStyleSheet("color: #94a3b8; font-size: 12px; line-height: 1.4;")
        layout.addWidget(header)
        layout.addWidget(sub)

        # Contenedor central: Lista interactiva a la izquierda + Botones de orden a la derecha
        center_layout = QHBoxLayout()
        center_layout.setSpacing(12)

        self.list_widget = QListWidget(self)
        self.list_widget.setDragEnabled(True)
        self.list_widget.setAcceptDrops(True)
        self.list_widget.setDropIndicatorShown(True)
        self.list_widget.setDragDropMode(QAbstractItemView.InternalMove)
        self.list_widget.setDefaultDropAction(Qt.MoveAction)
        self.list_widget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.list_widget.setStyleSheet(
            "QListWidget {"
            "    background-color: rgba(15, 23, 42, 0.65);"
            "    border: 1px solid rgba(255, 255, 255, 0.1);"
            "    border-radius: 8px;"
            "    padding: 6px;"
            "    color: #f1f5f9;"
            "    font-size: 12px;"
            "}"
            "QListWidget::item {"
            "    background-color: rgba(30, 41, 59, 0.5);"
            "    border: 1px solid rgba(255, 255, 255, 0.05);"
            "    border-radius: 6px;"
            "    padding: 7px 10px;"
            "    margin-bottom: 3px;"
            "    color: #f1f5f9;"
            "}"
            "QListWidget::item:hover {"
            "    background-color: rgba(56, 189, 248, 0.15);"
            "    border: 1px solid rgba(56, 189, 248, 0.3);"
            "}"
            "QListWidget::item:selected {"
            "    background-color: rgba(2, 132, 199, 0.4);"
            "    border: 1px solid #38bdf8;"
            "    color: #ffffff;"
            "}"
        )
        center_layout.addWidget(self.list_widget, stretch=1)

        # Panel lateral de botones de reordenación
        side_layout = QVBoxLayout()
        side_layout.setSpacing(8)

        lbl_order = QLabel("ORDEN")
        lbl_order.setStyleSheet("color: #38bdf8; font-weight: bold; font-size: 11px;")
        side_layout.addWidget(lbl_order)

        btn_top = QPushButton("⤒ Al Inicio")
        btn_top.setToolTip("Mover el elemento seleccionado al principio de la barra")
        btn_top.clicked.connect(self._move_to_top)
        side_layout.addWidget(btn_top)

        btn_up = QPushButton("▲ Subir")
        btn_up.setToolTip("Subir una posición")
        btn_up.clicked.connect(self._move_up)
        side_layout.addWidget(btn_up)

        btn_down = QPushButton("▼ Bajar")
        btn_down.setToolTip("Bajar una posición")
        btn_down.clicked.connect(self._move_down)
        side_layout.addWidget(btn_down)

        btn_bottom = QPushButton("⤓ Al Final")
        btn_bottom.setToolTip("Mover el elemento seleccionado al final de la barra")
        btn_bottom.clicked.connect(self._move_to_bottom)
        side_layout.addWidget(btn_bottom)

        side_layout.addSpacing(12)

        lbl_select = QLabel("SELECCIÓN")
        lbl_select.setStyleSheet("color: #38bdf8; font-weight: bold; font-size: 11px;")
        side_layout.addWidget(lbl_select)

        btn_select_all = QPushButton("☑ Marcar Todos")
        btn_select_all.clicked.connect(self._select_all)
        side_layout.addWidget(btn_select_all)

        btn_deselect_all = QPushButton("☐ Desmarcar Todos")
        btn_deselect_all.clicked.connect(self._deselect_all)
        side_layout.addWidget(btn_deselect_all)

        btn_reset = QPushButton("🔄 Predeterminados")
        btn_reset.setToolTip("Restablecer el orden y visibilidad por defecto")
        btn_reset.clicked.connect(self._reset_defaults)
        side_layout.addWidget(btn_reset)

        side_layout.addStretch()
        center_layout.addLayout(side_layout)
        layout.addLayout(center_layout)

        # Nota explicativa
        note_lbl = QLabel(
            "<span style='color:#94a3b8; font-size:11px;'>"
            "💡 <b>Nota:</b> El elemento <b>'↔ Espaciador flexible'</b> empuja los botones anteriores hacia la "
            "izquierda y los posteriores hacia la derecha de la ventana."
            "</span>"
        )
        note_lbl.setWordWrap(True)
        layout.addWidget(note_lbl)

        # Botones inferiores (Cancelar, Guardar)
        btns_layout = QHBoxLayout()
        btns_layout.addStretch()
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.clicked.connect(self.reject)
        btns_layout.addWidget(btn_cancel)

        btn_save = QPushButton("Guardar y Aplicar")
        btn_save.setObjectName("primaryBtn")
        btn_save.clicked.connect(self._save_and_apply)
        btns_layout.addWidget(btn_save)
        layout.addLayout(btns_layout)

        self._populate_list()

    def _populate_list(self):
        order, visibility = self.main_window._load_toolbar_config()
        self.list_widget.clear()
        for key in order:
            label = TOOLBAR_ITEM_LABELS.get(key, key)
            is_vis = visibility.get(key, DEFAULT_TOOLBAR_VISIBILITY.get(key, True))
            item = QListWidgetItem(label)
            item.setData(Qt.UserRole, key)
            item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsDragEnabled)
            item.setCheckState(Qt.Checked if is_vis else Qt.Unchecked)
            self.list_widget.addItem(item)

    def _move_up(self):
        row = self.list_widget.currentRow()
        if row > 0:
            item = self.list_widget.takeItem(row)
            self.list_widget.insertItem(row - 1, item)
            self.list_widget.setCurrentRow(row - 1)

    def _move_down(self):
        row = self.list_widget.currentRow()
        if 0 <= row < self.list_widget.count() - 1:
            item = self.list_widget.takeItem(row)
            self.list_widget.insertItem(row + 1, item)
            self.list_widget.setCurrentRow(row + 1)

    def _move_to_top(self):
        row = self.list_widget.currentRow()
        if row > 0:
            item = self.list_widget.takeItem(row)
            self.list_widget.insertItem(0, item)
            self.list_widget.setCurrentRow(0)

    def _move_to_bottom(self):
        row = self.list_widget.currentRow()
        if 0 <= row < self.list_widget.count() - 1:
            item = self.list_widget.takeItem(row)
            self.list_widget.insertItem(self.list_widget.count(), item)
            self.list_widget.setCurrentRow(self.list_widget.count() - 1)

    def _select_all(self):
        for i in range(self.list_widget.count()):
            self.list_widget.item(i).setCheckState(Qt.Checked)

    def _deselect_all(self):
        for i in range(self.list_widget.count()):
            self.list_widget.item(i).setCheckState(Qt.Unchecked)

    def _reset_defaults(self):
        self.list_widget.clear()
        for key in DEFAULT_TOOLBAR_ORDER:
            label = TOOLBAR_ITEM_LABELS.get(key, key)
            is_vis = DEFAULT_TOOLBAR_VISIBILITY.get(key, True)
            item = QListWidgetItem(label)
            item.setData(Qt.UserRole, key)
            item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsDragEnabled)
            item.setCheckState(Qt.Checked if is_vis else Qt.Unchecked)
            self.list_widget.addItem(item)

    def _save_and_apply(self):
        new_order = []
        new_visibility = {}
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            key = item.data(Qt.UserRole)
            new_order.append(key)
            new_visibility[key] = (item.checkState() == Qt.Checked)

        self.main_window._save_toolbar_config(new_order, new_visibility)
        self.accept()


DEFAULT_CONTEXT_MENU_ORDER = [
    "title",
    "open",
    "sep_playback",
    "play_pause",
    "seek_backward",
    "seek_forward",
    "stop",
    "sep_optical",
    "proj_menu",
    "stereo_menu",
    "toggle_eye",
    "fov_menu",
    "invert_menu",
    "speed_menu",
    "sep_tools",
    "recenter",
    "flip_x",
    "flip_y",
    "hud",
    "fullscreen",
    "sep_settings",
    "customize_context_menu",
    "customize_toolbar",
    "patterns",
    "shortcuts",
    "about",
]

DEFAULT_CONTEXT_MENU_VISIBILITY = {
    "title": True,
    "open": True,
    "sep_playback": True,
    "play_pause": True,
    "seek_backward": True,
    "seek_forward": True,
    "stop": True,
    "sep_optical": True,
    "proj_menu": True,
    "stereo_menu": True,
    "toggle_eye": True,
    "fov_menu": True,
    "invert_menu": True,
    "speed_menu": True,
    "sep_tools": True,
    "recenter": True,
    "flip_x": True,
    "flip_y": True,
    "hud": True,
    "fullscreen": True,
    "sep_settings": True,
    "customize_context_menu": True,
    "customize_toolbar": True,
    "patterns": True,
    "shortcuts": True,
    "about": True,
}

CONTEXT_MENU_ITEM_LABELS = {
    "title": "⚡ Encabezado / Título (OMNIVR PLAYER)",
    "open": "📂 Abrir Video... (Ctrl+O)",
    "sep_playback": "── Separador: Reproducción ──",
    "play_pause": "▶ / ⏸ Reproducir y Pausar (Espacio)",
    "seek_backward": "⏪ Retroceder 5 segundos (Izq)",
    "seek_forward": "⏩ Adelantar 5 segundos (Der)",
    "stop": "⏹ Detener y reiniciar al inicio (Home)",
    "sep_optical": "── Separador: Óptica y 3D ──",
    "proj_menu": "📷 Menú de Proyecciones 360 / VR",
    "stereo_menu": "🕶️ Menú de Modo 3D Estéreo (VR180 / 190 / 360)",
    "toggle_eye": "👁️ Alternar Ojo Izquierdo ⇄ Derecho (E)",
    "fov_menu": "🔍 Menú de Campo de Visión (FOV)",
    "invert_menu": "🔀 Menú de Inversión de Ejes",
    "speed_menu": "⚡ Menú de Velocidad de Reproducción",
    "sep_tools": "── Separador: Herramientas ──",
    "recenter": "🎯 Centrar Vista de Cámara (R)",
    "flip_x": "⇄ Invertir Horizontal (Espejo)",
    "flip_y": "⇅ Invertir Vertical",
    "hud": "ℹ️ HUD / Telemetría OSD en Pantalla (H)",
    "fullscreen": "⛶ / 🗗 Pantalla Completa (F / F11)",
    "sep_settings": "── Separador: Configuración ──",
    "customize_context_menu": "⚙️ Personalizar Menú Clic Derecho...",
    "customize_toolbar": "⚙️ Personalizar Barra de Controles...",
    "patterns": "🏷️ Reglas de Nombre de Archivo...",
    "shortcuts": "⌨️ Atajos de Teclado...",
    "about": "ℹ️ Acerca de OmniVR Player...",
}


class VRCustomizeContextMenuDialog(QDialog):
    """
    Diálogo Glassmorphic para Personalizar y Reordenar el Menú de Clic Derecho (Context Menu).
    Permite activar, ocultar y reordenar cualquier opción mediante arrastrar y soltar (Drag & Drop)
    o utilizando los botones Subir / Bajar.
    """
    def __init__(self, main_window, parent=None):
        super().__init__(parent or main_window)
        self.main_window = main_window
        self.setWindowTitle("Personalizar y Reordenar Menú de Clic Derecho")
        self.resize(600, 680)
        self.setStyleSheet(DARK_STYLESHEET)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        header = QLabel("⚙️ PERSONALIZAR Y REORDENAR MENÚ DE CLIC DERECHO")
        header.setStyleSheet("font-size: 16px; font-weight: bold; color: #38bdf8;")
        sub = QLabel(
            "• Active o desactive las casillas para mostrar u ocultar opciones del menú contextual.<br>"
            "• <b>Arrastre los elementos</b> con el ratón o use los botones <b>▲ / ▼</b> para cambiar su posición en el menú."
        )
        sub.setStyleSheet("color: #94a3b8; font-size: 12px; line-height: 1.4;")
        layout.addWidget(header)
        layout.addWidget(sub)

        # Contenedor central: Lista interactiva a la izquierda + Botones de orden a la derecha
        center_layout = QHBoxLayout()
        center_layout.setSpacing(12)

        self.list_widget = QListWidget(self)
        self.list_widget.setDragEnabled(True)
        self.list_widget.setAcceptDrops(True)
        self.list_widget.setDropIndicatorShown(True)
        self.list_widget.setDragDropMode(QAbstractItemView.InternalMove)
        self.list_widget.setDefaultDropAction(Qt.MoveAction)
        self.list_widget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.list_widget.setStyleSheet(
            "QListWidget {"
            "    background-color: rgba(15, 23, 42, 0.65);"
            "    border: 1px solid rgba(255, 255, 255, 0.1);"
            "    border-radius: 8px;"
            "    padding: 6px;"
            "    color: #f1f5f9;"
            "    font-size: 12px;"
            "}"
            "QListWidget::item {"
            "    background-color: rgba(30, 41, 59, 0.5);"
            "    border: 1px solid rgba(255, 255, 255, 0.05);"
            "    border-radius: 6px;"
            "    padding: 7px 10px;"
            "    margin-bottom: 3px;"
            "    color: #f1f5f9;"
            "}"
            "QListWidget::item:hover {"
            "    background-color: rgba(56, 189, 248, 0.15);"
            "    border: 1px solid rgba(56, 189, 248, 0.3);"
            "}"
            "QListWidget::item:selected {"
            "    background-color: rgba(2, 132, 199, 0.4);"
            "    border: 1px solid #38bdf8;"
            "    color: #ffffff;"
            "}"
        )
        center_layout.addWidget(self.list_widget, stretch=1)

        # Panel lateral de botones de reordenación
        side_layout = QVBoxLayout()
        side_layout.setSpacing(8)

        lbl_order = QLabel("ORDEN")
        lbl_order.setStyleSheet("color: #38bdf8; font-weight: bold; font-size: 11px;")
        side_layout.addWidget(lbl_order)

        btn_top = QPushButton("⤒ Al Inicio")
        btn_top.setToolTip("Mover la opción seleccionada al principio del menú")
        btn_top.clicked.connect(self._move_to_top)
        side_layout.addWidget(btn_top)

        btn_up = QPushButton("▲ Subir")
        btn_up.setToolTip("Subir una posición")
        btn_up.clicked.connect(self._move_up)
        side_layout.addWidget(btn_up)

        btn_down = QPushButton("▼ Bajar")
        btn_down.setToolTip("Bajar una posición")
        btn_down.clicked.connect(self._move_down)
        side_layout.addWidget(btn_down)

        btn_bottom = QPushButton("⤓ Al Final")
        btn_bottom.setToolTip("Mover la opción seleccionada al final del menú")
        btn_bottom.clicked.connect(self._move_to_bottom)
        side_layout.addWidget(btn_bottom)

        side_layout.addSpacing(12)

        lbl_select = QLabel("SELECCIÓN")
        lbl_select.setStyleSheet("color: #38bdf8; font-weight: bold; font-size: 11px;")
        side_layout.addWidget(lbl_select)

        btn_select_all = QPushButton("☑ Marcar Todos")
        btn_select_all.clicked.connect(self._select_all)
        side_layout.addWidget(btn_select_all)

        btn_deselect_all = QPushButton("☐ Desmarcar Todos")
        btn_deselect_all.clicked.connect(self._deselect_all)
        side_layout.addWidget(btn_deselect_all)

        btn_reset = QPushButton("🔄 Predeterminados")
        btn_reset.setToolTip("Restablecer el orden y visibilidad por defecto")
        btn_reset.clicked.connect(self._reset_defaults)
        side_layout.addWidget(btn_reset)

        side_layout.addStretch()
        center_layout.addLayout(side_layout)
        layout.addLayout(center_layout)

        # Nota explicativa
        note_lbl = QLabel(
            "<span style='color:#94a3b8; font-size:11px;'>"
            "💡 <b>Nota:</b> Los elementos <b>'── Separador ──'</b> añaden líneas divisorias visuales. "
            "Puede moverlos o desmarcarlos según su preferencia."
            "</span>"
        )
        note_lbl.setWordWrap(True)
        layout.addWidget(note_lbl)

        # Botones inferiores (Cancelar, Guardar)
        btns_layout = QHBoxLayout()
        btns_layout.addStretch()
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.clicked.connect(self.reject)
        btns_layout.addWidget(btn_cancel)

        btn_save = QPushButton("Guardar y Aplicar")
        btn_save.setObjectName("primaryBtn")
        btn_save.clicked.connect(self._save_and_apply)
        btns_layout.addWidget(btn_save)
        layout.addLayout(btns_layout)

        self._populate_list()

    def _populate_list(self):
        order, visibility = self.main_window._load_context_menu_config()
        self.list_widget.clear()
        for key in order:
            label = CONTEXT_MENU_ITEM_LABELS.get(key, key)
            is_vis = visibility.get(key, DEFAULT_CONTEXT_MENU_VISIBILITY.get(key, True))
            item = QListWidgetItem(label)
            item.setData(Qt.UserRole, key)
            item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsDragEnabled)
            item.setCheckState(Qt.Checked if is_vis else Qt.Unchecked)
            self.list_widget.addItem(item)

    def _move_up(self):
        row = self.list_widget.currentRow()
        if row > 0:
            item = self.list_widget.takeItem(row)
            self.list_widget.insertItem(row - 1, item)
            self.list_widget.setCurrentRow(row - 1)

    def _move_down(self):
        row = self.list_widget.currentRow()
        if 0 <= row < self.list_widget.count() - 1:
            item = self.list_widget.takeItem(row)
            self.list_widget.insertItem(row + 1, item)
            self.list_widget.setCurrentRow(row + 1)

    def _move_to_top(self):
        row = self.list_widget.currentRow()
        if row > 0:
            item = self.list_widget.takeItem(row)
            self.list_widget.insertItem(0, item)
            self.list_widget.setCurrentRow(0)

    def _move_to_bottom(self):
        row = self.list_widget.currentRow()
        if 0 <= row < self.list_widget.count() - 1:
            item = self.list_widget.takeItem(row)
            self.list_widget.insertItem(self.list_widget.count(), item)
            self.list_widget.setCurrentRow(self.list_widget.count() - 1)

    def _select_all(self):
        for i in range(self.list_widget.count()):
            self.list_widget.item(i).setCheckState(Qt.Checked)

    def _deselect_all(self):
        for i in range(self.list_widget.count()):
            self.list_widget.item(i).setCheckState(Qt.Unchecked)

    def _reset_defaults(self):
        self.list_widget.clear()
        for key in DEFAULT_CONTEXT_MENU_ORDER:
            label = CONTEXT_MENU_ITEM_LABELS.get(key, key)
            is_vis = DEFAULT_CONTEXT_MENU_VISIBILITY.get(key, True)
            item = QListWidgetItem(label)
            item.setData(Qt.UserRole, key)
            item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsDragEnabled)
            item.setCheckState(Qt.Checked if is_vis else Qt.Unchecked)
            self.list_widget.addItem(item)

    def _save_and_apply(self):
        new_order = []
        new_visibility = {}
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            key = item.data(Qt.UserRole)
            new_order.append(key)
            new_visibility[key] = (item.checkState() == Qt.Checked)

        self.main_window._save_context_menu_config(new_order, new_visibility)
        self.accept()


class VRShortcutsDialog(QDialog):
    """
    Diálogo Glassmorphic de Atajos de Teclado y Controles con alto contraste
    y tipografía perfectamente legible.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Atajos de Teclado y Controles")
        self.resize(640, 540)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        header = QLabel("⌨️ ATAJOS DE TECLADO Y CONTROLES VR")
        header.setStyleSheet("font-size: 16px; font-weight: bold; color: #38bdf8;")
        sub = QLabel("Guía de navegación rápida e interactividad 360° / VR (GoPro VR Player Edition)")
        sub.setStyleSheet("color: #94a3b8; font-size: 12px;")
        layout.addWidget(header)
        layout.addWidget(sub)

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background: transparent;")

        content = QWidget()
        c_layout = QVBoxLayout(content)
        c_layout.setSpacing(8)

        categories = [
            ("▶ Reproducción & Navegación Temporal", [
                ("Espacio", "Reproducir / Pausar video"),
                ("Flecha Izq / Der", "Retroceder / Adelantar 5 segundos"),
                ("Shift + Izq / Der", "Retroceder / Adelantar 10 segundos"),
                ("Inicio (Home)", "Reiniciar reproducción al inicio"),
                ("Flechas Arr / Abj", "Subir / Bajar volumen (+/- 5%)"),
                ("M", "Silenciar / Activar sonido (Mute)"),
            ]),
            ("🕶️ Modo Estéreo 3D & Selección de Ojo", [
                ("E", "Alternar Ojo Izquierdo ⇄ Ojo Derecho al instante (sin afectar reproducción)"),
            ]),
            ("📷 Proyecciones Ópticas & Orientación", [
                ("P", "Rotar cíclicamente la proyección (Rectilíneo → Planet → Fisheye → Panini → 360)"),
                ("1 - 5", "Selección directa de proyección (1: Rectilíneo, 2: Planet, 3: Fisheye, 4: Panini, 5: 360)"),
                ("R", "Restablecer orientación de cámara al frente (Centrar vista)"),
                ("I", "Invertir ambos ejes de navegación con el mouse (Inverted Axes)"),
                ("H", "Mostrar / Ocultar HUD y telemetría OSD en pantalla"),
                ("F / F11", "Alternar Pantalla Completa"),
            ]),
            ("🔍 Zoom & Campo de Visión (FOV)", [
                ("+ / =", "Acercar Zoom (Disminuir ángulo FOV)"),
                ("- / _", "Alejar Zoom (Aumentar ángulo FOV)"),
                ("0", "Restablecer FOV a 90° estándar"),
                ("Rueda del Ratón", "Zoom dinámico continuo del campo de visión (FOV)"),
            ]),
            ("🖱️ Control Interactivo con Ratón", [
                ("Clic Izquierdo", "Pausar / Reanudar reproducción (un solo clic sin arrastre)"),
                ("Arrastre Clic Izq", "Rotar ángulo de vista 360° en la esfera (Yaw y Pitch)"),
                ("Arrastre Clic Der", "Inclinación angular de cámara (Roll horizontal)"),
                ("Clic Derecho", "Abrir Menú Contextual (100% personalizable y reordenable)"),
                ("Clic Der en Barra", "Personalizar y reordenar botones de la barra inferior"),
                ("Doble Clic Izq", "Alternar Pantalla Completa"),
            ])
        ]

        for cat_title, items in categories:
            cat_lbl = QLabel(cat_title)
            cat_lbl.setStyleSheet("color: #38bdf8; font-size: 13px; font-weight: bold; margin-top: 8px; border-bottom: 1px solid rgba(56, 189, 248, 0.2); padding-bottom: 3px;")
            c_layout.addWidget(cat_lbl)
            for key, desc in items:
                row = QLabel(
                    f"<span style='color:#38bdf8; font-weight:bold; background:rgba(56,189,248,0.15); padding:2px 8px; border-radius:4px; font-family:Consolas;'>{key}</span> "
                    f"&nbsp;&nbsp; <span style='color:#f1f5f9; font-size:12px;'>{desc}</span>"
                )
                row.setStyleSheet("padding: 3px 0;")
                c_layout.addWidget(row)

        scroll.setWidget(content)
        layout.addWidget(scroll)

        btn = QPushButton("Entendido", self)
        btn.setObjectName("closeBtn")
        btn.clicked.connect(self.accept)
        layout.addWidget(btn, 0, Qt.AlignCenter)


class VRAboutDialog(QDialog):
    """Diálogo Acerca de OmniVR Player 8K con diseño moderno y alto contraste."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Acerca de OmniVR Player")
        self.resize(540, 440)

        layout = QVBoxLayout(self)
        layout.setSpacing(14)

        top_box = QVBoxLayout()
        title = QLabel("⚡ OmniVR Player 8K")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #38bdf8; letter-spacing: 0.5px;")
        edition = QLabel("Inspirado en GoPro VR Player 3.0.5")
        edition.setStyleSheet("font-size: 13px; color: #94a3b8; font-weight: 500;")
        top_box.addWidget(title)
        top_box.addWidget(edition)
        layout.addLayout(top_box)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background-color: rgba(56, 189, 248, 0.25); max-height: 1px; border: none;")
        layout.addWidget(line)

        features = [
            ("🚀 Decodificación por GPU Hardware", "Aceleración NVIDIA RTX NVDEC / D3D11VA para reproducción fluida de hasta 8K 60FPS sin pérdidas."),
            ("🕶️ Soporte Estéreo VR Integral", "Monoscópico 2D, VR 180° SBS, VR 190° SBS (Canon RF 5.2mm Dual Fisheye), 360° SBS y 360° Over-Under."),
            ("📷 Motores de Proyección Óptica", "Rectilíneo (estándar GoPro VR), Little Planet, Ojo de Pez Circular sin distorsión polar, Panini y 360° Esférico."),
            ("🏷️ Auto-Detección Inteligente", "Detección instantánea de proyecciones y lentes según nombres de archivo (8K_FISHEYE190, 180x180_3dh, 8K_LR_180, etc.) con reglas personalizables."),
            ("🎮 Inversión de Ejes & Roll", "Inversión independiente o simultánea de ejes Yaw/Pitch, rotación Roll con clic derecho y telemetría OSD.")
        ]

        for title_f, desc_f in features:
            row = QLabel(f"<b><span style='color:#38bdf8;'>{title_f}:</span></b> <span style='color:#cbd5e1; font-size:12px;'>{desc_f}</span>")
            row.setWordWrap(True)
            row.setStyleSheet("padding: 2px 0;")
            layout.addWidget(row)

        layout.addStretch()

        btn = QPushButton("Cerrar", self)
        btn.setObjectName("closeBtn")
        btn.clicked.connect(self.accept)
        layout.addWidget(btn, 0, Qt.AlignCenter)


class VRInViewportToolTip(QFrame):
    """
    Tooltip flotante in-viewport con estética Glassmorphic.
    Se renderiza directamente dentro de QOpenGLWidget para garantizar visibilidad al 100%
    en pantalla completa y compatibilidad absoluta con NVIDIA DirectFlip.
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("inViewportToolTip")
        self.setVisible(False)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(0)

        self.label = QLabel(self)
        self.label.setObjectName("inViewportToolTipText")
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

    def show_tip(self, text, widget):
        if not text:
            self.hide()
            return
        self.label.setText(text)
        self.adjustSize()

        parent = self.parentWidget()
        if not parent:
            return

        w = self.width()
        h = self.height()
        pos = widget.mapTo(parent, QPoint(0, 0))

        x = pos.x() + (widget.width() - w) // 2
        y = pos.y() - h - 6
        if y < 8:
            y = pos.y() + widget.height() + 6

        x = max(8, min(parent.width() - w - 8, x))
        y = max(8, min(parent.height() - h - 8, y))
        self.setGeometry(x, y, w, h)
        self.raise_()
        self.show()

    def show_tip_at_pos(self, text, rel_pos, widget):
        if not text:
            self.hide()
            return
        self.label.setText(text)
        self.adjustSize()

        parent = self.parentWidget()
        if not parent:
            return

        w = self.width()
        h = self.height()
        pos = widget.mapTo(parent, QPoint(0, 0))

        x = pos.x() + rel_pos.x() - w // 2
        y = pos.y() - h - 8
        if y < 8:
            y = pos.y() + widget.height() + 8

        x = max(8, min(parent.width() - w - 8, x))
        y = max(8, min(parent.height() - h - 8, y))
        self.setGeometry(x, y, w, h)
        self.raise_()
        self.show()

    def show_osd_message(self, text, duration_ms=1800):
        """Muestra un mensaje de telemetría/notificación flotante temporalmente centrado en pantalla."""
        if not text:
            self.hide()
            return
        self.label.setText(text)
        self.adjustSize()

        parent = self.parentWidget()
        if not parent:
            return

        w = self.width()
        h = self.height()
        x = (parent.width() - w) // 2
        y = 36
        self.setGeometry(x, y, w, h)
        self.raise_()
        self.show()

        self._osd_active = True
        if hasattr(self, '_osd_timer') and self._osd_timer:
            self._osd_timer.stop()
        self._osd_timer = QTimer(self)
        self._osd_timer.setSingleShot(True)

        def _on_timeout():
            self._osd_active = False
            self.hide()

        self._osd_timer.timeout.connect(_on_timeout)
        self._osd_timer.start(duration_ms)

    def hide_tip(self):
        if getattr(self, '_osd_active', False):
            return
        self.hide()


class ClickableSlider(QSlider):
    """Custom slider that seeks directly to clicked position and shows hover time preview."""
    sliderClicked = Signal(int)

    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        self.setMouseTracking(True)
        self.duration_sec = 0.0

    def set_duration(self, dur):
        self.duration_sec = max(0.0, float(dur))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            val = self._pos_to_val(event.position().x())
            self.setValue(val)
            self.sliderClicked.emit(val)
            event.accept()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.duration_sec > 0:
            val = self._pos_to_val(event.position().x())
            sec = (val / max(1, self.maximum())) * self.duration_sec
            m, s = divmod(int(sec), 60)
            h, m = divmod(m, 60)
            time_str = f"{h:02d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"
            win = self.window()
            if hasattr(win, 'in_viewport_tooltip'):
                win.in_viewport_tooltip.show_tip_at_pos(time_str, event.position().toPoint(), self)
            else:
                QToolTip.showText(event.globalPosition().toPoint(), time_str, self)
        super().mouseMoveEvent(event)

    def leaveEvent(self, event):
        win = self.window()
        if hasattr(win, 'in_viewport_tooltip'):
            win.in_viewport_tooltip.hide_tip()
        super().leaveEvent(event)

    def _pos_to_val(self, pos_x):
        w = max(1, self.width())
        ratio = max(0.0, min(1.0, pos_x / w))
        return int(self.minimum() + ratio * (self.maximum() - self.minimum()))


class VROverlayMenu(QFrame):
    """
    Menú desplegable y contextual flotante in-viewport con estética Glassmorphic.
    Se renderiza directamente dentro de QOpenGLWidget para garantizar visibilidad al 100%
    en ventana y pantalla completa, inmune a la superposición y DirectFlip de NVIDIA RTX.
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("vrOverlayMenu")
        self.setVisible(False)
        self._history = []
        self._current_builder = None
        self._anchor_widget = None
        self._anchor_pos = None

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(4, 4, 4, 4)
        outer_layout.setSpacing(0)

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setStyleSheet("background: transparent; border: none;")

        self.content_widget = QWidget()
        self.main_layout = QVBoxLayout(self.content_widget)
        self.main_layout.setContentsMargins(6, 6, 6, 6)
        self.main_layout.setSpacing(2)

        self.scroll_area.setWidget(self.content_widget)
        outer_layout.addWidget(self.scroll_area)

    def clear(self):
        while self.main_layout.count():
            item = self.main_layout.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)
                w.deleteLater()

    def add_title(self, title_text):
        lbl = QLabel(title_text, self.content_widget)
        lbl.setObjectName("overlayTitle")
        lbl.show()
        self.main_layout.addWidget(lbl)

    def add_action(self, text, callback, checked=False, shortcut=""):
        btn = QPushButton(self.content_widget)
        btn.setObjectName("overlayItem")
        prefix = "✔  " if checked else "    "
        sc_str = f"  ({shortcut})" if shortcut else ""
        btn.setText(f"{prefix}{text}{sc_str}")
        if checked:
            btn.setStyleSheet("font-weight: bold; color: #38bdf8;")
        def on_click():
            self.hide()
            callback()
        btn.clicked.connect(on_click)
        btn.show()
        self.main_layout.addWidget(btn)
        return btn

    def add_sub_nav(self, text, build_fn):
        btn = QPushButton(f"    {text}  ▸", self.content_widget)
        btn.setObjectName("overlayItem")
        btn.clicked.connect(lambda: self._navigate_to(build_fn))
        btn.show()
        self.main_layout.addWidget(btn)
        return btn

    def add_back_button(self, label="← Volver"):
        btn = QPushButton(label, self.content_widget)
        btn.setObjectName("overlayHeader")
        btn.clicked.connect(self._go_back)
        btn.show()
        self.main_layout.addWidget(btn)

    def add_separator(self):
        line = QFrame(self.content_widget)
        line.setObjectName("overlaySeparator")
        line.show()
        self.main_layout.addWidget(line)

    def _navigate_to(self, build_fn):
        self._history.append(self._current_builder)
        self._current_builder = build_fn
        self.clear()
        self.add_back_button()
        self.add_separator()
        build_fn(self)
        self._refit_geometry()

    def _go_back(self):
        if self._history:
            prev_fn = self._history.pop()
            self._current_builder = prev_fn
            self.clear()
            if self._history:
                self.add_back_button()
                self.add_separator()
            prev_fn(self)
            self._refit_geometry()
        else:
            self.hide()

    def show_builder(self, build_fn, anchor_pos=None, anchor_widget=None):
        self._history = []
        self._current_builder = build_fn
        self._anchor_pos = anchor_pos
        self._anchor_widget = anchor_widget
        self.clear()
        build_fn(self)
        self._refit_geometry()
        self.raise_()
        self.show()

    def _refit_geometry(self):
        for i in range(self.main_layout.count()):
            item = self.main_layout.itemAt(i)
            w = item.widget() if item else None
            if w:
                w.show()
        self.main_layout.activate()
        self.content_widget.adjustSize()

        parent = self.parentWidget()
        if not parent:
            return
        pw = parent.width()
        ph = parent.height()

        cw_hint = self.content_widget.sizeHint()
        desired_w = max(240, cw_hint.width() + 24)
        desired_h = cw_hint.height() + 16

        max_h = max(100, ph - 30)
        max_w = max(150, pw - 30)

        w = min(desired_w, max_w)
        h = min(desired_h, max_h)

        if self._anchor_widget:
            pos = self._anchor_widget.mapTo(parent, QPoint(0, 0))
            x = pos.x() + (self._anchor_widget.width() - w) // 2
            y = pos.y() - h - 8
            if y < 10:
                y = pos.y() + self._anchor_widget.height() + 8
        elif self._anchor_pos:
            x = self._anchor_pos.x()
            y = self._anchor_pos.y()
        else:
            x = (pw - w) // 2
            y = (ph - h) // 2

        x = max(10, min(pw - w - 10, x))
        y = max(10, min(ph - h - 10, y))
        self.setGeometry(x, y, w, h)
        self.raise_()


class VRMainWindow(QMainWindow):
    PROJECTIONS_ORDER = [
        VRGLWidget.PROJ_RECTILINEAR,
        VRGLWidget.PROJ_LITTLE_PLANET,
        VRGLWidget.PROJ_FISHEYE,
        VRGLWidget.PROJ_PANINI,
        VRGLWidget.PROJ_SPHERICAL_360
    ]

    def __init__(self, initial_video=None):
        super().__init__()
        self.setWindowTitle("OmniVR Player 8K — Reproductor VR GPU (GoPro VR Player Edition)")
        self.resize(1380, 840)
        self.setAcceptDrops(True)
        self.setStyleSheet(DARK_STYLESHEET)

        # Persistent Settings (QSettings)
        self.settings = QSettings("OmniVR", "OmniVRPlayer")
        self.pattern_manager = VRFilenamePatternManager(self.settings)

        # Fullscreen state tracking
        self._was_maximized = False

        # Initialize Backend & OpenGL Viewport
        self.backend = VRVideoBackend(self)
        self.viewport = VRGLWidget(self.backend, self)
        self.setCentralWidget(self.viewport)

        # Restore saved Inverted Axes preferences
        saved_inv_x = self.settings.value("invert_x", False, type=bool)
        saved_inv_y = self.settings.value("invert_y", False, type=bool)
        self.viewport.set_invert_x(saved_inv_x)
        self.viewport.set_invert_y(saved_inv_y)

        # Restore saved Dome FOV coverage preference (180°, 190°, 200°, 220°, 240°)
        saved_dome_fov = self.settings.value("dome_fov", 180.0, type=float)
        self.viewport.set_dome_fov_degrees(saved_dome_fov)

        # Restore saved lens optical model (0: Equirectangular, 1: Circular Fisheye / Canon RF 5.2mm)
        saved_lens_model = self.settings.value("lens_model", 0, type=int)
        self.viewport.set_lens_model(saved_lens_model)

        # Restore saved image orientation flip preferences
        saved_flip_x = self.settings.value("flip_x", False, type=bool)
        saved_flip_y = self.settings.value("flip_y", False, type=bool)
        self.viewport.flip_x = 1 if saved_flip_x else 0
        self.viewport.flip_y = 1 if saved_flip_y else 0

        # Build Desktop Menu Bar (GoPro VR Player Style)
        self._build_menu_bar()

        # Build In-Viewport Overlay Menu (Renders inside OpenGL framebuffer, 100% immune to NVIDIA DirectFlip)
        self.overlay_menu = VROverlayMenu(self.viewport)

        # Build In-Viewport ToolTip (Parented to viewport, 100% immune to NVIDIA DirectFlip)
        self.in_viewport_tooltip = VRInViewportToolTip(self.viewport)

        # Build Floating HUD Pill (Parented to viewport, NOT visible by default)
        self.hud_pill = self._build_hud_pill()

        # Build Floating Bottom Control Bar (Parented to viewport)
        self.bottom_bar = self._build_bottom_bar()

        # Build Welcome / Drag & Drop Card (Parented to viewport)
        self.welcome_card = self._build_welcome_card()

        # Synchronize UI with loaded settings
        self._sync_invert_ui()
        self._sync_flip_ui()

        # Audio mute state tracking
        self.is_muted = False
        self.pre_mute_volume = 100

        # UI Auto-hide timer (GoPro VR Player style)
        self.is_ui_visible = True
        self.hide_timer = QTimer(self)
        self.hide_timer.setInterval(3500)
        self.hide_timer.timeout.connect(self._auto_hide_ui)
        self.hide_timer.start()

        # Connect Signals & Setup Shortcuts
        self._connect_signals()
        self._setup_shortcuts()

        # Update initial positions
        self._reposition_overlays()

        # Load video if explicitly requested via sys.argv or argument
        if initial_video and os.path.exists(initial_video):
            QTimer.singleShot(400, lambda: self.load_video(initial_video))

    def _build_menu_bar(self):
        menubar = self.menuBar()

        # 1. Menú Archivo
        file_menu = menubar.addMenu("Archivo")
        act_open = file_menu.addAction("📂 Abrir Video...")
        act_open.setShortcut(QKeySequence("Ctrl+O"))
        act_open.triggered.connect(self._open_file_dialog)

        act_open_url = file_menu.addAction("🌐 Abrir URL de red...")
        act_open_url.setShortcut(QKeySequence("Ctrl+U"))
        act_open_url.triggered.connect(self._open_url_dialog)

        file_menu.addSeparator()

        act_demo_8k = file_menu.addAction("🪐 Cargar Demo 8K 360° (Equirectangular)")
        act_demo_8k.triggered.connect(self._load_demo_8k)

        act_demo_180 = file_menu.addAction("🕶️ Cargar Demo 4K VR180 SBS (3D Estéreo)")
        act_demo_180.triggered.connect(self._load_demo_180)

        act_demo_190 = file_menu.addAction("🕶️ Cargar Demo 4K VR190 SBS (Gran Domo / Canon)")
        act_demo_190.triggered.connect(self._load_demo_190)

        file_menu.addSeparator()

        act_exit = file_menu.addAction("Salir")
        act_exit.setShortcut(QKeySequence("Ctrl+Q"))
        act_exit.triggered.connect(self.close)

        # 2. Menú Reproducción
        play_menu = menubar.addMenu("Reproducción")
        self.act_play_pause = play_menu.addAction("⏯ Reproducir / Pausa")
        self.act_play_pause.setShortcut(QKeySequence(Qt.Key_Space))
        self.act_play_pause.triggered.connect(self.backend.toggle_play)

        act_prev5 = play_menu.addAction("⏪ Retroceder 5 seg")
        act_prev5.setShortcut(QKeySequence(Qt.Key_Left))
        act_prev5.triggered.connect(lambda: self.backend.seek(-5, absolute=False))

        act_next5 = play_menu.addAction("⏩ Adelantar 5 seg")
        act_next5.setShortcut(QKeySequence(Qt.Key_Right))
        act_next5.triggered.connect(lambda: self.backend.seek(5, absolute=False))

        act_prev10 = play_menu.addAction("⏪ Retroceder 10 seg")
        act_prev10.setShortcut(QKeySequence("Shift+Left"))
        act_prev10.triggered.connect(lambda: self.backend.seek(-10, absolute=False))

        act_next10 = play_menu.addAction("⏩ Adelantar 10 seg")
        act_next10.setShortcut(QKeySequence("Shift+Right"))
        act_next10.triggered.connect(lambda: self.backend.seek(10, absolute=False))

        act_restart = play_menu.addAction("⏹ Reiniciar al inicio")
        act_restart.setShortcut(QKeySequence(Qt.Key_Home))
        act_restart.triggered.connect(lambda: self.backend.seek(0, absolute=True))

        play_menu.addSeparator()

        self.act_loop = play_menu.addAction("🔁 Repetir en bucle")
        self.act_loop.setCheckable(True)
        self.act_loop.setShortcut(QKeySequence("Ctrl+L"))
        self.act_loop.toggled.connect(self._set_loop_state)

        # Submenú Velocidad
        speed_menu = play_menu.addMenu("⚡ Velocidad de Reproducción")
        self.speed_group = QActionGroup(self)
        for s in ["0.25x", "0.5x", "0.75x", "1.0x", "1.25x", "1.5x", "2.0x"]:
            a = speed_menu.addAction(s)
            a.setCheckable(True)
            if s == "1.0x":
                a.setChecked(True)
            self.speed_group.addAction(a)
            a.triggered.connect(lambda chk=False, sp=s: self._on_speed_selected(sp))

        # 3. Menú Proyección
        proj_menu = menubar.addMenu("Proyección")

        # Rotar siguiente proyección (Atajo P)
        self.act_cycle_proj = proj_menu.addAction("🔄 Rotar Siguiente Proyección (P)")
        self.act_cycle_proj.setShortcut(QKeySequence(Qt.Key_P))
        self.act_cycle_proj.triggered.connect(self._cycle_next_projection)

        proj_menu.addSeparator()

        self.proj_group = QActionGroup(self)
        projs = [
            ("📷 Rectilíneo (GoPro VR estándar)", VRGLWidget.PROJ_RECTILINEAR, "1"),
            ("🪐 Little Planet (Pequeño Planeta 360°)", VRGLWidget.PROJ_LITTLE_PLANET, "2"),
            ("🐟 Ojo de Pez (Fisheye 180°/360°)", VRGLWidget.PROJ_FISHEYE, "3"),
            ("🏛️ Panini (Cilíndrico Panorámico)", VRGLWidget.PROJ_PANINI, "4"),
            ("🌐 Esférico 360° (Equirectangular)", VRGLWidget.PROJ_SPHERICAL_360, "5"),
        ]
        self.proj_actions = {}
        for name, mode_id, sc in projs:
            a = proj_menu.addAction(name)
            a.setCheckable(True)
            a.setShortcut(QKeySequence(sc))
            if mode_id == VRGLWidget.PROJ_RECTILINEAR:
                a.setChecked(True)
            self.proj_group.addAction(a)
            self.proj_actions[mode_id] = a
            a.triggered.connect(lambda chk=False, m=mode_id: self._set_projection_mode(m))

        # 4. Menú Estereoscopía 3D (Opciones directas sin submenús confusos)
        stereo_menu = menubar.addMenu("Estéreo 3D")
        self.stereo_group = QActionGroup(self)

        self.act_stereo_mono = stereo_menu.addAction("2D Mono (Estándar)")
        self.act_stereo_mono.setCheckable(True)
        self.act_stereo_mono.setChecked(True)
        self.stereo_group.addAction(self.act_stereo_mono)
        self.act_stereo_mono.triggered.connect(lambda: self._set_stereo_mode(VRGLWidget.STEREO_MONO))

        stereo_menu.addSeparator()

        self.act_stereo_180 = stereo_menu.addAction("🕶️ VR 180° SBS")
        self.act_stereo_180.setCheckable(True)
        self.stereo_group.addAction(self.act_stereo_180)
        self.act_stereo_180.triggered.connect(self._set_vr180_preset)

        self.act_stereo_190 = stereo_menu.addAction("🕶️ VR 190° SBS")
        self.act_stereo_190.setCheckable(True)
        self.stereo_group.addAction(self.act_stereo_190)
        self.act_stereo_190.triggered.connect(self._set_vr190_preset)

        self.act_stereo_360_sbs = stereo_menu.addAction("🕶️ 360° SBS")
        self.act_stereo_360_sbs.setCheckable(True)
        self.stereo_group.addAction(self.act_stereo_360_sbs)
        self.act_stereo_360_sbs.triggered.connect(lambda: self._set_stereo_mode(VRGLWidget.STEREO_360_SBS_LEFT))

        self.act_stereo_360_ou = stereo_menu.addAction("🕶️ 360° Over-Under")
        self.act_stereo_360_ou.setCheckable(True)
        self.stereo_group.addAction(self.act_stereo_360_ou)
        self.act_stereo_360_ou.triggered.connect(lambda: self._set_stereo_mode(VRGLWidget.STEREO_360_OU_TOP))

        stereo_menu.addSeparator()

        self.eye_group = QActionGroup(self)
        self.eye_group.setExclusive(True)

        self.act_eye_left = stereo_menu.addAction("👁️ Ojo Izquierdo")
        self.act_eye_left.setCheckable(True)
        self.act_eye_left.setChecked(True)
        self.eye_group.addAction(self.act_eye_left)
        self.act_eye_left.triggered.connect(self._select_left_eye)

        self.act_eye_right = stereo_menu.addAction("👁️ Ojo Derecho")
        self.act_eye_right.setCheckable(True)
        self.eye_group.addAction(self.act_eye_right)
        self.act_eye_right.triggered.connect(self._select_right_eye)

        self.act_toggle_eye = stereo_menu.addAction("🔄 Alternar Ojo (Izq ⇄ Der)")
        self.act_toggle_eye.setShortcut(QKeySequence(Qt.Key_E))
        self.act_toggle_eye.triggered.connect(self._toggle_stereo_eye)

        stereo_menu.addSeparator()

        self.act_stereo_dual = stereo_menu.addAction("👓 Dual Estéreo (Visor VR / HMD)")
        self.act_stereo_dual.setCheckable(True)
        self.act_stereo_dual.triggered.connect(self._toggle_dual_stereo)

        self.act_stereo_invert = stereo_menu.addAction("🔄 Invertir Canales Dual (Der / Izq)")
        self.act_stereo_invert.setCheckable(True)
        self.act_stereo_invert.triggered.connect(self._toggle_invert_eyes)

        # 5. Menú Herramientas & Vista
        view_menu = menubar.addMenu("Herramientas")
        act_recenter = view_menu.addAction("🎯 Centrar Cámara")
        act_recenter.setShortcut(QKeySequence(Qt.Key_R))
        act_recenter.triggered.connect(self.viewport.recenter_view)

        self.act_orbit = view_menu.addAction("🔄 Giro Automático 360°")
        self.act_orbit.setCheckable(True)
        self.act_orbit.triggered.connect(self._toggle_auto_orbit)

        # Inverted Axes separado (GoPro VR Player style) con guardado persistente
        axes_menu = view_menu.addMenu("🔀 Inversión de Ejes (Inverted Axes)")
        self.act_inv_x = axes_menu.addAction("☑ Invertir Eje Horizontal (X / Yaw)")
        self.act_inv_x.setCheckable(True)
        self.act_inv_x.toggled.connect(self._toggle_invert_x)

        self.act_inv_y = axes_menu.addAction("☑ Invertir Eje Vertical (Y / Pitch)")
        self.act_inv_y.setCheckable(True)
        self.act_inv_y.toggled.connect(self._toggle_invert_y)

        axes_menu.addSeparator()

        self.act_inv_both = axes_menu.addAction("Invertir Ambos Ejes (I)")
        self.act_inv_both.setShortcut(QKeySequence(Qt.Key_I))
        self.act_inv_both.triggered.connect(self._toggle_invert_both)

        self.act_flip_x = view_menu.addAction("⇄ Invertir Orientación Horizontal de Imagen (Espejo)")
        self.act_flip_x.setCheckable(True)
        self.act_flip_x.triggered.connect(self._toggle_flip_x)

        self.act_flip_y = view_menu.addAction("⇅ Invertir Orientación Vertical de Imagen")
        self.act_flip_y.setCheckable(True)
        self.act_flip_y.triggered.connect(self._toggle_flip_y)

        # Campo de Visión (FOV) Personalizable
        fov_menu = view_menu.addMenu("🔍 Campo de Visión (FOV)")
        act_zin = fov_menu.addAction("🔍 Acercar Zoom (+)")
        act_zin.triggered.connect(lambda: self.viewport.zoom_in(5.0))
        act_zout = fov_menu.addAction("🔍 Alejar Zoom (-)")
        act_zout.triggered.connect(lambda: self.viewport.zoom_out(5.0))
        act_zres = fov_menu.addAction("🎯 Restablecer FOV a 90° (0)")
        act_zres.triggered.connect(self.viewport.reset_fov)
        fov_menu.addSeparator()
        for deg in [240, 220, 200, 190, 180, 140, 120, 105, 90, 75, 60, 45]:
            fov_menu.addAction(f"{deg}°").triggered.connect(lambda chk=False, d=deg: self.viewport.set_fov_degrees(d))
        fov_menu.addSeparator()
        act_cust_fov = fov_menu.addAction("⚙️ Personalizar FOV (Grados exactos)...")
        act_cust_fov.triggered.connect(self._dialog_custom_fov)

        # HUD Telemetría (Default No Visible)
        self.act_hud_toggle = view_menu.addAction("ℹ️ HUD / Telemetría OSD")
        self.act_hud_toggle.setCheckable(True)
        self.act_hud_toggle.setChecked(False)
        self.act_hud_toggle.setShortcut(QKeySequence(Qt.Key_H))
        self.act_hud_toggle.triggered.connect(self._toggle_hud)

        view_menu.addSeparator()

        self.act_fs = view_menu.addAction("⛶ Pantalla Completa")
        self.act_fs.setShortcut(QKeySequence(Qt.Key_F))
        self.act_fs.triggered.connect(self._toggle_fullscreen)

        # Calidad GPU
        qual_menu = view_menu.addMenu("🎮 Calidad GPU de Decodificación")
        qual_group = QActionGroup(self)
        quals = [
            ("8K Nativo (7680x3840)", VRGLWidget.QUALITY_NATIVE_8K),
            ("4K Ultra (3840x1920)", VRGLWidget.QUALITY_ULTRA_4K),
            ("Adaptativo (Resolución Display)", VRGLWidget.QUALITY_ADAPTIVE)
        ]
        for q_name, q_mode in quals:
            a = qual_menu.addAction(q_name)
            a.setCheckable(True)
            if q_mode == VRGLWidget.QUALITY_NATIVE_8K:
                a.setChecked(True)
            qual_group.addAction(a)
            a.triggered.connect(lambda chk=False, m=q_mode: self.viewport.set_quality_mode(m))

        view_menu.addSeparator()
        act_cust_toolbar = view_menu.addAction("⚙️ Personalizar y Reordenar Barra de Controles...")
        act_cust_toolbar.triggered.connect(self._show_customize_toolbar_dialog)

        act_cust_context_menu = view_menu.addAction("⚙️ Personalizar Menú de Clic Derecho...")
        act_cust_context_menu.triggered.connect(self._show_customize_context_menu_dialog)

        act_patterns = view_menu.addAction("🏷️ Configurar Detección por Nombre de Archivo...")
        act_patterns.triggered.connect(self._show_patterns_dialog)

        # 6. Menú Ayuda
        help_menu = menubar.addMenu("Ayuda")
        act_shortcuts = help_menu.addAction("⌨️ Atajos de Teclado...")
        act_shortcuts.triggered.connect(self._show_shortcuts_dialog)

        act_about = help_menu.addAction("ℹ️ Acerca de OmniVR Player...")
        act_about.triggered.connect(self._show_about_dialog)

        # Registrar acciones con atajo en la ventana principal para asegurar que
        # funcionen tanto en modo ventana como en pantalla completa con barra de menú oculta
        for action in [
            act_open, act_open_url, act_exit, self.act_play_pause,
            act_prev5, act_next5, act_prev10, act_next10, act_restart,
            self.act_loop, self.act_cycle_proj, act_recenter,
            self.act_inv_both, self.act_hud_toggle, self.act_fs,
            self.act_toggle_eye
        ]:
            self.addAction(action)
        for act in self.proj_actions.values():
            self.addAction(act)

    def show_osd_banner(self, text, duration_ms=1800):
        """Muestra un banner OSD flotante estilizado en pantalla sin interrumpir la reproducción."""
        if hasattr(self, 'in_viewport_tooltip') and self.in_viewport_tooltip:
            self.in_viewport_tooltip.show_osd_message(text, duration_ms)

    def _build_hud_pill(self):
        pill = QFrame(self.viewport)
        pill.setObjectName("hudPill")
        layout = QVBoxLayout(pill)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(4)

        self.hud_label = QLabel(pill)
        self.hud_label.setStyleSheet("line-height: 1.4; color: #f1f5f9; font-size: 11px;")
        self.hud_label.setText(
            "<b>OmniVR 8K Player</b> — <i>GPU NVDEC [RTX 5090]</i><br>"
            "Resolución: Sin video | Códec: -<br>"
            "Orientación: Yaw: 0.0° | Pitch: 0.0° | FOV: 90.0°<br>"
            "Proyección: Rectilíneo | Modo 3D: Mono 2D"
        )
        layout.addWidget(self.hud_label)
        pill.adjustSize()
        # Telemetría NO visible por defecto como solicitó el usuario
        pill.setVisible(False)
        return pill

    def _build_welcome_card(self):
        card = QFrame(self.viewport)
        card.setObjectName("welcomeCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(14)
        layout.setAlignment(Qt.AlignCenter)

        title = QLabel("⚡ OmniVR Player 8K", card)
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #38bdf8; letter-spacing: 0.5px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("Reproductor de Video 360° / VR con Aceleración por GPU\nInspirado en GoPro VR Player 3.0.5", card)
        subtitle.setStyleSheet("font-size: 13px; color: #94a3b8;")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)

        info = QLabel("Arrastre y suelte cualquier video 360° aquí o seleccione un archivo:", card)
        info.setStyleSheet("font-size: 12px; color: #cbd5e1; margin-top: 8px;")
        info.setAlignment(Qt.AlignCenter)
        layout.addWidget(info)

        btn_box = QHBoxLayout()
        btn_box.setSpacing(10)

        btn_open = QPushButton("📂 Abrir Video...", card)
        btn_open.setStyleSheet("background-color: #0284c7; font-size: 13px; font-weight: bold; padding: 7px 16px;")
        btn_open.clicked.connect(self._open_file_dialog)
        btn_box.addWidget(btn_open)

        btn_demo_8k = QPushButton("🪐 Demo 8K 360°", card)
        btn_demo_8k.setStyleSheet("padding: 7px 14px;")
        btn_demo_8k.clicked.connect(self._load_demo_8k)
        btn_box.addWidget(btn_demo_8k)

        btn_demo_180 = QPushButton("🕶️ Demo VR180 SBS", card)
        btn_demo_180.setStyleSheet("padding: 7px 14px;")
        btn_demo_180.clicked.connect(self._load_demo_180)
        btn_box.addWidget(btn_demo_180)

        btn_demo_190 = QPushButton("🕶️ Demo VR190 SBS", card)
        btn_demo_190.setStyleSheet("padding: 7px 14px;")
        btn_demo_190.clicked.connect(self._load_demo_190)
        btn_box.addWidget(btn_demo_190)

        layout.addLayout(btn_box)
        card.adjustSize()
        return card

    def _build_bottom_bar(self):
        bar = QFrame(self.viewport)
        bar.setObjectName("bottomControlBar")
        main_layout = QVBoxLayout(bar)
        main_layout.setContentsMargins(16, 8, 16, 10)
        main_layout.setSpacing(6)

        # -------------------------------------------------------------
        # Fila Superior: Timeline Seek Bar con tiempo interactivo
        # -------------------------------------------------------------
        timeline_layout = QHBoxLayout()
        timeline_layout.setSpacing(10)

        self.cur_time_label = QLabel("00:00:00", bar)
        self.cur_time_label.setObjectName("timeLabel")
        timeline_layout.addWidget(self.cur_time_label)

        self.seek_slider = ClickableSlider(Qt.Horizontal, bar)
        self.seek_slider.setObjectName("seekSlider")
        self.seek_slider.setRange(0, 1000)
        self.seek_slider.sliderMoved.connect(self._on_seek_moved)
        self.seek_slider.sliderReleased.connect(self._on_seek_released)
        self.seek_slider.sliderClicked.connect(self._on_seek_clicked)
        timeline_layout.addWidget(self.seek_slider)

        self.total_time_label = QLabel("00:00:00", bar)
        self.total_time_label.setObjectName("timeLabel")
        timeline_layout.addWidget(self.total_time_label)

        main_layout.addLayout(timeline_layout)

        # -------------------------------------------------------------
        # Fila Inferior: Controles de reproducción, volumen, menús GoPro
        # -------------------------------------------------------------
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(6)
        self.controls_layout = controls_layout

        # 1. Botón Abrir Archivo
        self.btn_open = QToolButton(bar)
        self.btn_open.setObjectName("iconBtn")
        self.btn_open.setText("📁")
        self.btn_open.setToolTip("Abrir archivo de video (Ctrl+O)")
        self.btn_open.clicked.connect(self._open_file_dialog)

        # 2. Botón Retroceder 5s
        self.btn_prev5 = QPushButton("⏪ 5s", bar)
        self.btn_prev5.setToolTip("Retroceder 5 segundos (Flecha Izq)")
        self.btn_prev5.clicked.connect(lambda: self.backend.seek(-5, absolute=False))

        # 3. Botón Play / Pause Circular Grande
        self.btn_play = QPushButton("▶", bar)
        self.btn_play.setObjectName("playButton")
        self.btn_play.setToolTip("Reproducir / Pausar (Espacio)")
        self.btn_play.clicked.connect(self.backend.toggle_play)

        # 4. Botón Adelantar 5s
        self.btn_next5 = QPushButton("5s ⏩", bar)
        self.btn_next5.setToolTip("Adelantar 5 segundos (Flecha Der)")
        self.btn_next5.clicked.connect(lambda: self.backend.seek(5, absolute=False))

        # 5. Botón Detener / Inicio
        self.btn_stop = QToolButton(bar)
        self.btn_stop.setObjectName("iconBtn")
        self.btn_stop.setText("⏹")
        self.btn_stop.setToolTip("Reiniciar al inicio (Home)")
        self.btn_stop.clicked.connect(lambda: self.backend.seek(0, absolute=True))

        # 6. Control de Volumen con Mute
        self.btn_volume = QToolButton(bar)
        self.btn_volume.setObjectName("iconBtn")
        self.btn_volume.setText("🔊")
        self.btn_volume.setToolTip("Silenciar / Activar sonido (M)")
        self.btn_volume.clicked.connect(self._toggle_mute)

        self.vol_slider = ClickableSlider(Qt.Horizontal, bar)
        self.vol_slider.setObjectName("volSlider")
        self.vol_slider.setRange(0, 100)
        self.vol_slider.setValue(100)
        self.vol_slider.setFixedWidth(75)
        self.vol_slider.setToolTip("Volumen: 100%")
        self.vol_slider.valueChanged.connect(self._on_volume_changed)

        # 7. Menú Proyecciones (GoPro VR Player Style)
        self.btn_proj_menu = QToolButton(bar)
        self.btn_proj_menu.setObjectName("menuBtn")
        self.btn_proj_menu.setText("📷 Proyección ▾")
        self.btn_proj_menu.setToolTip("Seleccionar proyección 360 / VR (Teclas 1 - 5, o P para rotar)")
        self.btn_proj_menu.clicked.connect(self._show_proj_menu)

        # 8. Menú Modo 3D Estereoscópico (Sin anaglifo)
        self.btn_stereo_menu = QToolButton(bar)
        self.btn_stereo_menu.setObjectName("menuBtn")
        self.btn_stereo_menu.setText("🕶️ 3D ▾")
        self.btn_stereo_menu.setToolTip("Seleccionar modo estereoscópico VR180 / 360")
        self.btn_stereo_menu.clicked.connect(self._show_stereo_menu)

        # 9. Menú Velocidad
        self.btn_speed_menu = QToolButton(bar)
        self.btn_speed_menu.setObjectName("menuBtn")
        self.btn_speed_menu.setText("⚡ 1.0x ▾")
        self.btn_speed_menu.setToolTip("Velocidad de reproducción")
        self.btn_speed_menu.clicked.connect(self._show_speed_menu)

        # 10. Control de FOV (Campo de Visión) Personalizable
        self.btn_fov = QToolButton(bar)
        self.btn_fov.setObjectName("menuBtn")
        self.btn_fov.setText("🔍 90° ▾")
        self.btn_fov.setToolTip("Campo de visión (FOV) / Zoom (+ / - / 0)")
        self.btn_fov.clicked.connect(self._show_fov_menu)

        # 11. Botón Repetición en bucle
        self.btn_loop = QToolButton(bar)
        self.btn_loop.setObjectName("iconBtn")
        self.btn_loop.setText("🔁")
        self.btn_loop.setCheckable(True)
        self.btn_loop.setToolTip("Repetición en bucle (Ctrl+L)")
        self.btn_loop.toggled.connect(self._set_loop_state)

        # 12. Botón Centrar cámara
        self.btn_recenter = QToolButton(bar)
        self.btn_recenter.setObjectName("iconBtn")
        self.btn_recenter.setText("🎯")
        self.btn_recenter.setToolTip("Restablecer orientación de cámara (R)")
        self.btn_recenter.clicked.connect(self.viewport.recenter_view)

        # 13. Botón Alternar Ojo Izquierdo ⇄ Derecho (Eye Toggle)
        self.btn_toggle_eye = QToolButton(bar)
        self.btn_toggle_eye.setObjectName("iconBtn")
        self.btn_toggle_eye.setText("👁️")
        self.btn_toggle_eye.setToolTip("Alternar Ojo Izquierdo ⇄ Derecho (E)")
        self.btn_toggle_eye.clicked.connect(self._toggle_stereo_eye)

        # 14. Botón Rotación Automática
        self.btn_orbit = QToolButton(bar)
        self.btn_orbit.setObjectName("iconBtn")
        self.btn_orbit.setText("🔄")
        self.btn_orbit.setCheckable(True)
        self.btn_orbit.setToolTip("Activar rotación automática 360°")
        self.btn_orbit.toggled.connect(self._toggle_auto_orbit)

        # 15. Botón Inversión de Ejes
        self.btn_invert_axes = QToolButton(bar)
        self.btn_invert_axes.setObjectName("iconBtn")
        self.btn_invert_axes.setText("🔀")
        self.btn_invert_axes.setCheckable(True)
        self.btn_invert_axes.setToolTip("Inversión de ejes (I)")
        self.btn_invert_axes.clicked.connect(self._show_invert_menu)

        # 16. Botón HUD Telemetría
        self.btn_hud_btn = QToolButton(bar)
        self.btn_hud_btn.setObjectName("iconBtn")
        self.btn_hud_btn.setText("ℹ️")
        self.btn_hud_btn.setCheckable(True)
        self.btn_hud_btn.setChecked(False)
        self.btn_hud_btn.setToolTip("Mostrar/Ocultar OSD y Telemetría (H)")
        self.btn_hud_btn.clicked.connect(self._toggle_hud)

        # 17. Invertir orientación horizontal
        self.btn_flip_x_btn = QToolButton(bar)
        self.btn_flip_x_btn.setObjectName("iconBtn")
        self.btn_flip_x_btn.setText("⇄")
        self.btn_flip_x_btn.setCheckable(True)
        self.btn_flip_x_btn.setToolTip("Invertir orientación horizontal de imagen (Espejo)")
        self.btn_flip_x_btn.toggled.connect(self._toggle_flip_x)

        # 18. Invertir orientación vertical
        self.btn_flip_btn = QToolButton(bar)
        self.btn_flip_btn.setObjectName("iconBtn")
        self.btn_flip_btn.setText("⇅")
        self.btn_flip_btn.setCheckable(True)
        self.btn_flip_btn.setToolTip("Invertir orientación vertical de imagen")
        self.btn_flip_btn.toggled.connect(self._toggle_flip_y)

        # 19. Pantalla Completa
        self.btn_fullscreen = QToolButton(bar)
        self.btn_fullscreen.setObjectName("iconBtn")
        self.btn_fullscreen.setText("⛶")
        self.btn_fullscreen.setToolTip("Pantalla completa (F / F11)")
        self.btn_fullscreen.clicked.connect(self._toggle_fullscreen)

        # 20. Badge GPU 8K
        self.badge_label = QLabel("⚡ 8K NVDEC", bar)
        self.badge_label.setObjectName("badgeLabel")

        # Disponer widgets en el layout según configuración de orden y visibilidad
        self._apply_toolbar_layout()

        main_layout.addLayout(self.controls_layout)
        self._install_tooltip_filter(bar)

        # Context menu para personalizar la barra con clic derecho
        bar.setContextMenuPolicy(Qt.CustomContextMenu)
        bar.customContextMenuRequested.connect(self._show_toolbar_context_menu)

        return bar

    def _load_toolbar_config(self):
        saved_order = self.settings.value("toolbar_order", None)
        saved_vis = self.settings.value("toolbar_visibility", None)

        # 1. Cargar Orden
        order = list(DEFAULT_TOOLBAR_ORDER)
        if isinstance(saved_order, str):
            try:
                parsed = json.loads(saved_order)
                if isinstance(parsed, list):
                    saved_order = parsed
            except Exception:
                saved_order = None

        if isinstance(saved_order, list):
            valid_keys = set(DEFAULT_TOOLBAR_ORDER)
            order = [k for k in saved_order if k in valid_keys]
            # Asegurar que cualquier control que falte se agregue al final
            for k in DEFAULT_TOOLBAR_ORDER:
                if k not in order:
                    order.append(k)

        # 2. Cargar Visibilidad
        vis = dict(DEFAULT_TOOLBAR_VISIBILITY)
        if isinstance(saved_vis, str):
            try:
                parsed_v = json.loads(saved_vis)
                if isinstance(parsed_v, dict):
                    saved_vis = parsed_v
            except Exception:
                saved_vis = None

        if isinstance(saved_vis, dict):
            vis.update(saved_vis)

        return order, vis

    def _save_toolbar_config(self, order, visibility):
        self.settings.setValue("toolbar_order", json.dumps(order))
        self.settings.setValue("toolbar_visibility", json.dumps(visibility))
        self.settings.sync()
        self._apply_toolbar_layout(order, visibility)
        self.show_osd_banner("⚙️ Barra de controles actualizada")

    def _apply_toolbar_layout(self, order=None, visibility=None):
        if not hasattr(self, 'controls_layout') or self.controls_layout is None:
            return
        if order is None or visibility is None:
            loaded_order, loaded_vis = self._load_toolbar_config()
            if order is None:
                order = loaded_order
            if visibility is None:
                visibility = loaded_vis

        # Limpiar todos los items del layout (sin destruir los widgets)
        while self.controls_layout.count() > 0:
            self.controls_layout.takeAt(0)

        # Re-agregar en el orden especificado por el usuario
        for key in order:
            is_vis = visibility.get(key, DEFAULT_TOOLBAR_VISIBILITY.get(key, True))
            if key == "spacer":
                if is_vis:
                    self.controls_layout.addStretch()
            elif key == "volume_group":
                if hasattr(self, 'btn_volume') and hasattr(self, 'vol_slider'):
                    self.btn_volume.setVisible(bool(is_vis))
                    self.vol_slider.setVisible(bool(is_vis))
                    self.controls_layout.addWidget(self.btn_volume)
                    self.controls_layout.addWidget(self.vol_slider)
            else:
                w = getattr(self, key, None)
                if w is not None:
                    w.setVisible(bool(is_vis))
                    self.controls_layout.addWidget(w)

    def _load_toolbar_visibility(self):
        _, vis = self._load_toolbar_config()
        return vis

    def _save_toolbar_visibility(self, vis):
        order, _ = self._load_toolbar_config()
        self._save_toolbar_config(order, vis)

    def _apply_toolbar_visibility(self, vis=None):
        self._apply_toolbar_layout(visibility=vis)

    def _show_toolbar_context_menu(self, pos):
        menu = QMenu(self)
        menu.setStyleSheet(DARK_STYLESHEET)
        act = menu.addAction("⚙️ Personalizar y Reordenar Barra...")
        act.triggered.connect(self._show_customize_toolbar_dialog)
        menu.exec(self.bottom_bar.mapToGlobal(pos))

    def _show_customize_toolbar_dialog(self):
        dlg = VRCustomizeToolbarDialog(self, self)
        dlg.exec()

    def _load_context_menu_config(self):
        saved_order = self.settings.value("context_menu_order", None)
        saved_vis = self.settings.value("context_menu_visibility", None)

        order = list(DEFAULT_CONTEXT_MENU_ORDER)
        if isinstance(saved_order, str):
            try:
                parsed = json.loads(saved_order)
                if isinstance(parsed, list):
                    saved_order = parsed
            except Exception:
                saved_order = None

        if isinstance(saved_order, list):
            valid_keys = set(DEFAULT_CONTEXT_MENU_ORDER)
            order = [k for k in saved_order if k in valid_keys]
            for k in DEFAULT_CONTEXT_MENU_ORDER:
                if k not in order:
                    order.append(k)

        vis = dict(DEFAULT_CONTEXT_MENU_VISIBILITY)
        if isinstance(saved_vis, str):
            try:
                parsed_v = json.loads(saved_vis)
                if isinstance(parsed_v, dict):
                    saved_vis = parsed_v
            except Exception:
                saved_vis = None

        if isinstance(saved_vis, dict):
            vis.update(saved_vis)

        return order, vis

    def _save_context_menu_config(self, order, visibility):
        self.settings.setValue("context_menu_order", json.dumps(order))
        self.settings.setValue("context_menu_visibility", json.dumps(visibility))
        self.settings.sync()
        self.show_osd_banner("⚙️ Menú de clic derecho actualizado")

    def _show_customize_context_menu_dialog(self):
        dlg = VRCustomizeContextMenuDialog(self, self)
        dlg.exec()

    # -----------------------------------------------------------------
    # Desplegables de la Barra Inferior (In-Viewport VROverlayMenu)
    # -----------------------------------------------------------------
    def _show_proj_menu(self):
        if self.overlay_menu.isVisible() and self.overlay_menu._anchor_widget == self.btn_proj_menu:
            self.overlay_menu.hide()
            return
        self.overlay_menu.show_builder(self._build_proj_menu, anchor_widget=self.btn_proj_menu)

    def _show_stereo_menu(self):
        if self.overlay_menu.isVisible() and self.overlay_menu._anchor_widget == self.btn_stereo_menu:
            self.overlay_menu.hide()
            return
        self.overlay_menu.show_builder(self._build_stereo_menu, anchor_widget=self.btn_stereo_menu)

    def _show_speed_menu(self):
        if self.overlay_menu.isVisible() and self.overlay_menu._anchor_widget == self.btn_speed_menu:
            self.overlay_menu.hide()
            return
        self.overlay_menu.show_builder(self._build_speed_menu, anchor_widget=self.btn_speed_menu)

    def _show_fov_menu(self):
        if self.overlay_menu.isVisible() and self.overlay_menu._anchor_widget == self.btn_fov:
            self.overlay_menu.hide()
            return
        self.overlay_menu.show_builder(self._build_fov_menu, anchor_widget=self.btn_fov)

    def _show_invert_menu(self):
        if self.overlay_menu.isVisible() and self.overlay_menu._anchor_widget == self.btn_invert_axes:
            self.overlay_menu.hide()
            return
        self.overlay_menu.show_builder(self._build_invert_menu, anchor_widget=self.btn_invert_axes)

    # Constructores de Menú para VROverlayMenu (visibles en ventana y pantalla completa)
    def _build_proj_menu(self, menu):
        menu.add_title("📷 PROYECCIÓN 360 / VR")
        menu.add_action("🔄 Rotar Siguiente Proyección", self._cycle_next_projection, shortcut="P")
        menu.add_separator()
        cur_p = self.viewport.projection_mode
        projs = [
            ("📷 Rectilíneo (GoPro VR estándar)", VRGLWidget.PROJ_RECTILINEAR, "1"),
            ("🪐 Little Planet (Pequeño Planeta)", VRGLWidget.PROJ_LITTLE_PLANET, "2"),
            ("🐟 Ojo de Pez (Fisheye)", VRGLWidget.PROJ_FISHEYE, "3"),
            ("🏛️ Panini (Cilíndrico Panorámico)", VRGLWidget.PROJ_PANINI, "4"),
            ("🌐 Esférico 360° (Equirectangular)", VRGLWidget.PROJ_SPHERICAL_360, "5"),
        ]
        for name, pid, sc in projs:
            menu.add_action(name, lambda m=pid: self._set_projection_mode(m), checked=(cur_p == pid), shortcut=sc)

    def _build_stereo_menu(self, menu):
        menu.add_title("🕶️ MODO ESTEREOSCÓPICO 3D")
        cur_s = self.viewport.stereo_mode
        cur_dome = int(round(self.viewport.get_dome_fov_degrees()))

        is_mono = (cur_s == VRGLWidget.STEREO_MONO)
        is_180 = (cur_s in [VRGLWidget.STEREO_VR180_SBS_LEFT, VRGLWidget.STEREO_VR180_SBS_RIGHT] and cur_dome != 190)
        is_190 = (cur_s in [VRGLWidget.STEREO_VR180_SBS_LEFT, VRGLWidget.STEREO_VR180_SBS_RIGHT] and cur_dome == 190)
        is_360_sbs = (cur_s in [VRGLWidget.STEREO_360_SBS_LEFT, VRGLWidget.STEREO_360_SBS_RIGHT])
        is_360_ou = (cur_s in [VRGLWidget.STEREO_360_OU_TOP, VRGLWidget.STEREO_360_OU_BOTTOM])
        is_dual = (cur_s in [VRGLWidget.STEREO_VR180_SBS_DUAL, VRGLWidget.STEREO_360_SBS_DUAL, VRGLWidget.STEREO_360_OU_DUAL])
        is_inv = (cur_s in [VRGLWidget.STEREO_VR180_SBS_INVERTED, VRGLWidget.STEREO_360_SBS_INVERTED, VRGLWidget.STEREO_360_OU_INVERTED])

        menu.add_action("2D Mono (Estándar)", lambda: self._set_stereo_mode(VRGLWidget.STEREO_MONO), checked=is_mono)
        menu.add_separator()
        menu.add_action("🕶️ VR 180° SBS", self._set_vr180_preset, checked=is_180)
        menu.add_action("🕶️ VR 190° SBS", self._set_vr190_preset, checked=is_190)
        menu.add_action("🕶️ 360° SBS", lambda: self._set_stereo_mode(VRGLWidget.STEREO_360_SBS_RIGHT if self._is_right_eye_selected() else VRGLWidget.STEREO_360_SBS_LEFT), checked=is_360_sbs)
        menu.add_action("🕶️ 360° Over-Under", lambda: self._set_stereo_mode(VRGLWidget.STEREO_360_OU_BOTTOM if self._is_right_eye_selected() else VRGLWidget.STEREO_360_OU_TOP), checked=is_360_ou)
        menu.add_separator()
        is_left = (cur_s in [VRGLWidget.STEREO_VR180_SBS_LEFT, VRGLWidget.STEREO_360_SBS_LEFT, VRGLWidget.STEREO_360_OU_TOP])
        is_right = (cur_s in [VRGLWidget.STEREO_VR180_SBS_RIGHT, VRGLWidget.STEREO_360_SBS_RIGHT, VRGLWidget.STEREO_360_OU_BOTTOM])
        menu.add_action("👁️ Ojo Izquierdo", self._select_left_eye, checked=is_left)
        menu.add_action("👁️ Ojo Derecho", self._select_right_eye, checked=is_right)
        menu.add_action("🔄 Alternar Ojo (Izq ⇄ Der)", self._toggle_stereo_eye, shortcut="E")
        menu.add_separator()
        menu.add_action("👓 Dual Estéreo (Visor VR / HMD)", self._toggle_dual_stereo, checked=is_dual)
        menu.add_action("🔄 Invertir Canales en Dual", self._toggle_invert_eyes, checked=is_inv)

    def _build_speed_menu(self, menu):
        menu.add_title("⚡ VELOCIDAD DE REPRODUCCIÓN")
        cur_sp = getattr(self.backend.mpv_player, 'speed', 1.0) if self.backend.mpv_player else 1.0
        for s in ["0.25x", "0.5x", "0.75x", "1.0x", "1.25x", "1.5x", "2.0x"]:
            val = float(s.replace("x", ""))
            menu.add_action(s, lambda sp=s: self._on_speed_selected(sp), checked=abs(cur_sp - val) < 0.05)

    def _build_fov_menu(self, menu):
        menu.add_title("🔍 CAMPO DE VISIÓN (FOV)")
        menu.add_action("🔍 Acercar Zoom (+)", lambda: self.viewport.zoom_in(5.0), shortcut="+")
        menu.add_action("🔍 Alejar Zoom (-)", lambda: self.viewport.zoom_out(5.0), shortcut="-")
        menu.add_action("🎯 Restablecer FOV a 90° (0)", self.viewport.reset_fov, shortcut="0")
        menu.add_separator()
        cur_deg = int(round(math.degrees(self.viewport.fov)))
        presets = [
            ("240° (Ultra Panorámico / Little Planet)", 240),
            ("220° (Little Planet / Fisheye)", 220),
            ("200° (Super Fisheye)", 200),
            ("190° (Gran Domo 190°)", 190),
            ("180° (Hemisférico / Fisheye)", 180),
            ("140° (Ultra Gran Angular)", 140),
            ("120° (Gran Angular)", 120),
            ("105° (Gran Angular Medio)", 105),
            ("90° (Estándar GoPro VR)", 90),
            ("75° (Medio)", 75),
            ("60° (Primer Plano)", 60),
            ("45° (Telefoto)", 45),
        ]
        for name, deg in presets:
            menu.add_action(name, lambda d=deg: self.viewport.set_fov_degrees(d), checked=(cur_deg == deg))
        menu.add_separator()
        menu.add_action("⚙️ Personalizar FOV...", self._dialog_custom_fov)

    def _build_invert_menu(self, menu):
        menu.add_title("🔀 INVERSIÓN DE EJES (INVERTED AXES)")
        menu.add_action("Invertir Eje Horizontal (X / Yaw)", lambda: self._toggle_invert_x(), checked=self.viewport.invert_x)
        menu.add_action("Invertir Eje Vertical (Y / Pitch)", lambda: self._toggle_invert_y(), checked=self.viewport.invert_y)
        menu.add_separator()
        menu.add_action("Invertir Ambos Ejes", self._toggle_invert_both, shortcut="I")

    def _build_context_menu(self, menu):
        order, vis = self._load_context_menu_config()

        has_added_any = False
        last_was_separator = True  # Evitar separador al principio

        for key in order:
            if not vis.get(key, DEFAULT_CONTEXT_MENU_VISIBILITY.get(key, True)):
                continue

            if key == "title":
                menu.add_title("⚡ OMNIVR PLAYER")
                has_added_any = True
                last_was_separator = False
            elif key.startswith("sep_"):
                if has_added_any and not last_was_separator:
                    menu.add_separator()
                    last_was_separator = True
            elif key == "open":
                menu.add_action("📂 Abrir Video...", self._open_file_dialog, shortcut="Ctrl+O")
                has_added_any = True
                last_was_separator = False
            elif key == "play_pause":
                p_text = "⏸ Pausar" if not self.backend.is_paused else "▶ Reproducir"
                menu.add_action(p_text, self.backend.toggle_play, shortcut="Espacio")
                has_added_any = True
                last_was_separator = False
            elif key == "seek_backward":
                menu.add_action("⏪ -5 seg", lambda: self.backend.seek(-5, absolute=False), shortcut="Izq")
                has_added_any = True
                last_was_separator = False
            elif key == "seek_forward":
                menu.add_action("⏩ +5 seg", lambda: self.backend.seek(5, absolute=False), shortcut="Der")
                has_added_any = True
                last_was_separator = False
            elif key == "stop":
                menu.add_action("⏹ Reiniciar al inicio", lambda: self.backend.seek(0, absolute=True), shortcut="Home")
                has_added_any = True
                last_was_separator = False
            elif key == "proj_menu":
                menu.add_sub_nav("📷 Proyección", self._build_proj_menu)
                has_added_any = True
                last_was_separator = False
            elif key == "stereo_menu":
                menu.add_sub_nav("🕶️ Modo 3D Estéreo", self._build_stereo_menu)
                has_added_any = True
                last_was_separator = False
            elif key == "toggle_eye":
                is_right = self._is_right_eye_selected()
                eye_text = "👁️ Alternar a Ojo Izquierdo" if is_right else "👁️ Alternar a Ojo Derecho"
                menu.add_action(eye_text, self._toggle_stereo_eye, shortcut="E")
                has_added_any = True
                last_was_separator = False
            elif key == "fov_menu":
                menu.add_sub_nav("🔍 Campo de Visión (FOV)", self._build_fov_menu)
                has_added_any = True
                last_was_separator = False
            elif key == "invert_menu":
                menu.add_sub_nav("🔀 Inversión de Ejes", self._build_invert_menu)
                has_added_any = True
                last_was_separator = False
            elif key == "speed_menu":
                menu.add_sub_nav("⚡ Velocidad", self._build_speed_menu)
                has_added_any = True
                last_was_separator = False
            elif key == "recenter":
                menu.add_action("🎯 Centrar Vista", self.viewport.recenter_view, shortcut="R")
                has_added_any = True
                last_was_separator = False
            elif key == "flip_x":
                menu.add_action("⇄ Invertir Orientación Horizontal (Espejo)", self._toggle_flip_x, checked=bool(self.viewport.flip_x))
                has_added_any = True
                last_was_separator = False
            elif key == "flip_y":
                menu.add_action("⇅ Invertir Orientación Vertical", self._toggle_flip_y, checked=bool(self.viewport.flip_y))
                has_added_any = True
                last_was_separator = False
            elif key == "hud":
                menu.add_action("ℹ️ HUD / Telemetría OSD", self._toggle_hud, checked=self.hud_pill.isVisible(), shortcut="H")
                has_added_any = True
                last_was_separator = False
            elif key == "fullscreen":
                fs_text = "🗗 Salir de Pantalla Completa" if self.isFullScreen() else "⛶ Pantalla Completa"
                menu.add_action(fs_text, self._toggle_fullscreen, shortcut="F")
                has_added_any = True
                last_was_separator = False
            elif key == "customize_context_menu":
                menu.add_action("⚙️ Personalizar Menú Clic Derecho...", self._show_customize_context_menu_dialog)
                has_added_any = True
                last_was_separator = False
            elif key == "customize_toolbar":
                menu.add_action("⚙️ Personalizar Barra de Controles...", self._show_customize_toolbar_dialog)
                has_added_any = True
                last_was_separator = False
            elif key == "patterns":
                menu.add_action("🏷️ Patrones de Nombre de Archivo...", self._show_patterns_dialog)
                has_added_any = True
                last_was_separator = False
            elif key == "shortcuts":
                menu.add_action("⌨️ Atajos de Teclado...", self._show_shortcuts_dialog)
                has_added_any = True
                last_was_separator = False
            elif key == "about":
                menu.add_action("ℹ️ Acerca de OmniVR Player...", self._show_about_dialog)
                has_added_any = True
                last_was_separator = False

    def _dialog_custom_fov(self):
        cur_fov = int(round(math.degrees(self.viewport.fov)))
        min_deg, max_deg, _ = self.viewport.get_fov_limits()
        val, ok = QInputDialog.getInt(
            self,
            "Personalizar Campo de Visión (FOV)",
            f"Ingrese el ángulo FOV en grados ({int(min_deg)}° - {int(max_deg)}°):",
            cur_fov,
            int(min_deg),
            int(max_deg),
            1
        )
        if ok:
            self.viewport.set_fov_degrees(val)

    def _set_dome_fov(self, deg):
        self.viewport.set_dome_fov_degrees(deg)
        self.settings.setValue("dome_fov", float(deg))
        self.settings.sync()
        self._update_hud()

    def _dialog_custom_dome_fov(self):
        cur_dome = int(round(self.viewport.get_dome_fov_degrees()))
        val, ok = QInputDialog.getInt(
            self,
            "Personalizar Cobertura de Cúpula (Dome FOV)",
            "Ingrese el ángulo de cobertura de la cúpula/lente en grados (90° - 360°):",
            cur_dome,
            90,
            360,
            1
        )
        if ok:
            self._set_dome_fov(val)

    def _set_lens_model(self, model: int):
        self.viewport.set_lens_model(model)
        self.settings.setValue("lens_model", int(model))
        self.settings.sync()
        if hasattr(self, 'lens_model_actions'):
            for m, act in self.lens_model_actions.items():
                act.setChecked(m == model)
        self._update_hud()

    def _is_right_eye_selected(self):
        """Devuelve True si actualmente se está visualizando el ojo derecho (o inferior en OU)."""
        return self.viewport.stereo_mode in [
            VRGLWidget.STEREO_VR180_SBS_RIGHT,
            VRGLWidget.STEREO_360_SBS_RIGHT,
            VRGLWidget.STEREO_360_OU_BOTTOM,
            VRGLWidget.STEREO_VR180_SBS_INVERTED,
            VRGLWidget.STEREO_360_SBS_INVERTED,
            VRGLWidget.STEREO_360_OU_INVERTED
        ]

    def _select_left_eye(self):
        """Selecciona el ojo izquierdo (o superior en 360 OU) de forma inmediata en GPU."""
        cur = self.viewport.stereo_mode
        if cur == VRGLWidget.STEREO_VR180_SBS_RIGHT:
            self._set_stereo_mode(VRGLWidget.STEREO_VR180_SBS_LEFT)
        elif cur == VRGLWidget.STEREO_360_SBS_RIGHT:
            self._set_stereo_mode(VRGLWidget.STEREO_360_SBS_LEFT)
        elif cur == VRGLWidget.STEREO_360_OU_BOTTOM:
            self._set_stereo_mode(VRGLWidget.STEREO_360_OU_TOP)
        elif cur == VRGLWidget.STEREO_VR180_SBS_INVERTED:
            self._set_stereo_mode(VRGLWidget.STEREO_VR180_SBS_DUAL)
        elif cur == VRGLWidget.STEREO_360_SBS_INVERTED:
            self._set_stereo_mode(VRGLWidget.STEREO_360_SBS_DUAL)
        elif cur == VRGLWidget.STEREO_360_OU_INVERTED:
            self._set_stereo_mode(VRGLWidget.STEREO_360_OU_DUAL)
        elif cur == VRGLWidget.STEREO_MONO:
            self._set_stereo_mode(VRGLWidget.STEREO_VR180_SBS_LEFT)
        self.show_osd_banner("👁️ Ojo Seleccionado: IZQUIERDO (Left Eye)")

    def _select_right_eye(self):
        """Selecciona el ojo derecho (o inferior en 360 OU) de forma inmediata en GPU."""
        cur = self.viewport.stereo_mode
        if cur in [VRGLWidget.STEREO_VR180_SBS_LEFT, VRGLWidget.STEREO_MONO]:
            self._set_stereo_mode(VRGLWidget.STEREO_VR180_SBS_RIGHT)
        elif cur == VRGLWidget.STEREO_360_SBS_LEFT:
            self._set_stereo_mode(VRGLWidget.STEREO_360_SBS_RIGHT)
        elif cur == VRGLWidget.STEREO_360_OU_TOP:
            self._set_stereo_mode(VRGLWidget.STEREO_360_OU_BOTTOM)
        elif cur == VRGLWidget.STEREO_VR180_SBS_DUAL:
            self._set_stereo_mode(VRGLWidget.STEREO_VR180_SBS_INVERTED)
        elif cur == VRGLWidget.STEREO_360_SBS_DUAL:
            self._set_stereo_mode(VRGLWidget.STEREO_360_SBS_INVERTED)
        elif cur == VRGLWidget.STEREO_360_OU_DUAL:
            self._set_stereo_mode(VRGLWidget.STEREO_360_OU_INVERTED)
        self.show_osd_banner("👁️ Ojo Seleccionado: DERECHO (Right Eye)")

    def _toggle_stereo_eye(self):
        """
        Alterna en caliente entre Ojo Izquierdo ⇄ Ojo Derecho en tiempo real.
        Operación 100% en shader GPU (0 ms, sin pausas, sin recarga de video y sin desincronización).
        """
        cur = self.viewport.stereo_mode
        if cur in [VRGLWidget.STEREO_VR180_SBS_LEFT, VRGLWidget.STEREO_MONO]:
            self._set_stereo_mode(VRGLWidget.STEREO_VR180_SBS_RIGHT)
            self.show_osd_banner("👁️ Ojo Activo: DERECHO (Right Eye)")
        elif cur == VRGLWidget.STEREO_VR180_SBS_RIGHT:
            self._set_stereo_mode(VRGLWidget.STEREO_VR180_SBS_LEFT)
            self.show_osd_banner("👁️ Ojo Activo: IZQUIERDO (Left Eye)")
        elif cur == VRGLWidget.STEREO_360_SBS_LEFT:
            self._set_stereo_mode(VRGLWidget.STEREO_360_SBS_RIGHT)
            self.show_osd_banner("👁️ Ojo Activo: DERECHO (Right Eye)")
        elif cur == VRGLWidget.STEREO_360_SBS_RIGHT:
            self._set_stereo_mode(VRGLWidget.STEREO_360_SBS_LEFT)
            self.show_osd_banner("👁️ Ojo Activo: IZQUIERDO (Left Eye)")
        elif cur == VRGLWidget.STEREO_360_OU_TOP:
            self._set_stereo_mode(VRGLWidget.STEREO_360_OU_BOTTOM)
            self.show_osd_banner("👁️ Ojo Activo: INFERIOR / DERECHO")
        elif cur == VRGLWidget.STEREO_360_OU_BOTTOM:
            self._set_stereo_mode(VRGLWidget.STEREO_360_OU_TOP)
            self.show_osd_banner("👁️ Ojo Activo: SUPERIOR / IZQUIERDO")
        elif cur == VRGLWidget.STEREO_VR180_SBS_DUAL:
            self._set_stereo_mode(VRGLWidget.STEREO_VR180_SBS_INVERTED)
            self.show_osd_banner("🔄 Dual Estéreo: Canales Invertidos")
        elif cur == VRGLWidget.STEREO_VR180_SBS_INVERTED:
            self._set_stereo_mode(VRGLWidget.STEREO_VR180_SBS_DUAL)
            self.show_osd_banner("👓 Dual Estéreo: Canales Normales")
        elif cur == VRGLWidget.STEREO_360_SBS_DUAL:
            self._set_stereo_mode(VRGLWidget.STEREO_360_SBS_INVERTED)
            self.show_osd_banner("🔄 Dual Estéreo: Canales Invertidos")
        elif cur == VRGLWidget.STEREO_360_SBS_INVERTED:
            self._set_stereo_mode(VRGLWidget.STEREO_360_SBS_DUAL)
            self.show_osd_banner("👓 Dual Estéreo: Canales Normales")
        elif cur == VRGLWidget.STEREO_360_OU_DUAL:
            self._set_stereo_mode(VRGLWidget.STEREO_360_OU_INVERTED)
            self.show_osd_banner("🔄 Dual Estéreo: Canales Invertidos")
        elif cur == VRGLWidget.STEREO_360_OU_INVERTED:
            self._set_stereo_mode(VRGLWidget.STEREO_360_OU_DUAL)
            self.show_osd_banner("👓 Dual Estéreo: Canales Normales")

    def _set_vr180_preset(self):
        """Activa VR 180° SBS estándar."""
        self._set_dome_fov(180.0)
        self._set_lens_model(0)
        self._set_stereo_mode(VRGLWidget.STEREO_VR180_SBS_LEFT)

    def _set_vr190_preset(self):
        """Preajuste directo con 1 clic para videos VR 190° SBS (Canon Dual Fisheye / Gran Domo)."""
        self._set_dome_fov(190.0)
        self._set_lens_model(1)  # Activar Ojo de Pez Circular nativo para eliminar distorsión polar / pico
        self._set_stereo_mode(VRGLWidget.STEREO_VR180_SBS_LEFT)

    def _toggle_dual_stereo(self):
        cur = self.viewport.stereo_mode
        if cur in [VRGLWidget.STEREO_VR180_SBS_DUAL, VRGLWidget.STEREO_360_SBS_DUAL, VRGLWidget.STEREO_360_OU_DUAL,
                   VRGLWidget.STEREO_VR180_SBS_INVERTED, VRGLWidget.STEREO_360_SBS_INVERTED, VRGLWidget.STEREO_360_OU_INVERTED]:
            if cur in [VRGLWidget.STEREO_VR180_SBS_DUAL, VRGLWidget.STEREO_VR180_SBS_INVERTED]:
                self._set_stereo_mode(VRGLWidget.STEREO_VR180_SBS_LEFT)
            elif cur in [VRGLWidget.STEREO_360_SBS_DUAL, VRGLWidget.STEREO_360_SBS_INVERTED]:
                self._set_stereo_mode(VRGLWidget.STEREO_360_SBS_LEFT)
            else:
                self._set_stereo_mode(VRGLWidget.STEREO_360_OU_TOP)
        else:
            if cur in [VRGLWidget.STEREO_VR180_SBS_LEFT, VRGLWidget.STEREO_VR180_SBS_RIGHT]:
                self._set_stereo_mode(VRGLWidget.STEREO_VR180_SBS_DUAL)
            elif cur in [VRGLWidget.STEREO_360_SBS_LEFT, VRGLWidget.STEREO_360_SBS_RIGHT]:
                self._set_stereo_mode(VRGLWidget.STEREO_360_SBS_DUAL)
            elif cur in [VRGLWidget.STEREO_360_OU_TOP, VRGLWidget.STEREO_360_OU_BOTTOM]:
                self._set_stereo_mode(VRGLWidget.STEREO_360_OU_DUAL)
            else:
                self._set_stereo_mode(VRGLWidget.STEREO_VR180_SBS_DUAL)

    def _toggle_invert_eyes(self):
        cur = self.viewport.stereo_mode
        if cur in [VRGLWidget.STEREO_VR180_SBS_DUAL, VRGLWidget.STEREO_360_SBS_DUAL, VRGLWidget.STEREO_360_OU_DUAL]:
            if cur == VRGLWidget.STEREO_VR180_SBS_DUAL:
                self._set_stereo_mode(VRGLWidget.STEREO_VR180_SBS_INVERTED)
            elif cur == VRGLWidget.STEREO_360_SBS_DUAL:
                self._set_stereo_mode(VRGLWidget.STEREO_360_SBS_INVERTED)
            else:
                self._set_stereo_mode(VRGLWidget.STEREO_360_OU_INVERTED)
            self.show_osd_banner("🔄 Dual Estéreo: Canales Invertidos")
        elif cur in [VRGLWidget.STEREO_VR180_SBS_INVERTED, VRGLWidget.STEREO_360_SBS_INVERTED, VRGLWidget.STEREO_360_OU_INVERTED]:
            if cur == VRGLWidget.STEREO_VR180_SBS_INVERTED:
                self._set_stereo_mode(VRGLWidget.STEREO_VR180_SBS_DUAL)
            elif cur == VRGLWidget.STEREO_360_SBS_INVERTED:
                self._set_stereo_mode(VRGLWidget.STEREO_360_SBS_DUAL)
            else:
                self._set_stereo_mode(VRGLWidget.STEREO_360_OU_DUAL)
            self.show_osd_banner("👓 Dual Estéreo: Canales Normales")
        else:
            self._toggle_stereo_eye()

    def _cycle_next_projection(self):
        """Atajo con tecla P para rotar a la siguiente proyección de manera cíclica."""
        cur = self.viewport.projection_mode
        if cur in self.PROJECTIONS_ORDER:
            idx = (self.PROJECTIONS_ORDER.index(cur) + 1) % len(self.PROJECTIONS_ORDER)
        else:
            idx = 0
        next_mode = self.PROJECTIONS_ORDER[idx]
        self._set_projection_mode(next_mode)

    def _set_projection_mode(self, mode_id):
        self.viewport.set_projection(mode_id)
        if mode_id in self.proj_actions:
            self.proj_actions[mode_id].setChecked(True)
        names = {
            VRGLWidget.PROJ_RECTILINEAR: "Rectilíneo",
            VRGLWidget.PROJ_LITTLE_PLANET: "Little Planet",
            VRGLWidget.PROJ_FISHEYE: "Ojo de Pez",
            VRGLWidget.PROJ_PANINI: "Panini",
            VRGLWidget.PROJ_SPHERICAL_360: "360° Esférico"
        }
        self.btn_proj_menu.setText(f"📷 {names.get(mode_id, 'Proyección')} ▾")
        self._update_hud()

    def _set_stereo_mode(self, mode_id):
        self.viewport.set_stereo_mode(mode_id)
        cur_dome = int(round(self.viewport.get_dome_fov_degrees()))

        if hasattr(self, 'act_stereo_mono'):
            self.act_stereo_mono.setChecked(mode_id == VRGLWidget.STEREO_MONO)
        if hasattr(self, 'act_stereo_180'):
            self.act_stereo_180.setChecked(mode_id in [VRGLWidget.STEREO_VR180_SBS_LEFT, VRGLWidget.STEREO_VR180_SBS_RIGHT] and cur_dome != 190)
        if hasattr(self, 'act_stereo_190'):
            self.act_stereo_190.setChecked(mode_id in [VRGLWidget.STEREO_VR180_SBS_LEFT, VRGLWidget.STEREO_VR180_SBS_RIGHT] and cur_dome == 190)
        if hasattr(self, 'act_stereo_360_sbs'):
            self.act_stereo_360_sbs.setChecked(mode_id in [VRGLWidget.STEREO_360_SBS_LEFT, VRGLWidget.STEREO_360_SBS_RIGHT])
        if hasattr(self, 'act_stereo_360_ou'):
            self.act_stereo_360_ou.setChecked(mode_id in [VRGLWidget.STEREO_360_OU_TOP, VRGLWidget.STEREO_360_OU_BOTTOM])

        is_left = mode_id in [VRGLWidget.STEREO_VR180_SBS_LEFT, VRGLWidget.STEREO_360_SBS_LEFT, VRGLWidget.STEREO_360_OU_TOP]
        is_right = mode_id in [VRGLWidget.STEREO_VR180_SBS_RIGHT, VRGLWidget.STEREO_360_SBS_RIGHT, VRGLWidget.STEREO_360_OU_BOTTOM]
        if hasattr(self, 'act_eye_left'):
            self.act_eye_left.setChecked(is_left)
            self.act_eye_left.setEnabled(mode_id != VRGLWidget.STEREO_MONO)
        if hasattr(self, 'act_eye_right'):
            self.act_eye_right.setChecked(is_right)
            self.act_eye_right.setEnabled(mode_id != VRGLWidget.STEREO_MONO)

        if hasattr(self, 'btn_toggle_eye'):
            if is_right:
                self.btn_toggle_eye.setStyleSheet("color: #38bdf8; font-weight: bold;")
                self.btn_toggle_eye.setToolTip("Ojo actual: DERECHO. Clic para alternar a Izquierdo (E)")
            else:
                self.btn_toggle_eye.setStyleSheet("")
                self.btn_toggle_eye.setToolTip("Ojo actual: IZQUIERDO. Clic para alternar a Derecho (E)")

        if hasattr(self, 'act_stereo_dual'):
            self.act_stereo_dual.setChecked(mode_id in [VRGLWidget.STEREO_VR180_SBS_DUAL, VRGLWidget.STEREO_360_SBS_DUAL, VRGLWidget.STEREO_360_OU_DUAL])
        if hasattr(self, 'act_stereo_invert'):
            self.act_stereo_invert.setChecked(mode_id in [VRGLWidget.STEREO_VR180_SBS_INVERTED, VRGLWidget.STEREO_360_SBS_INVERTED, VRGLWidget.STEREO_360_OU_INVERTED])

        names = {
            VRGLWidget.STEREO_MONO: "2D Mono",
            VRGLWidget.STEREO_VR180_SBS_LEFT: "VR180 Izq",
            VRGLWidget.STEREO_VR180_SBS_RIGHT: "VR180 Der",
            VRGLWidget.STEREO_VR180_SBS_DUAL: "VR180 Dual",
            VRGLWidget.STEREO_VR180_SBS_INVERTED: "VR180 Invert",
            VRGLWidget.STEREO_360_SBS_LEFT: "360 SBS Izq",
            VRGLWidget.STEREO_360_SBS_RIGHT: "360 SBS Der",
            VRGLWidget.STEREO_360_SBS_DUAL: "360 SBS Dual",
            VRGLWidget.STEREO_360_SBS_INVERTED: "360 Invert",
            VRGLWidget.STEREO_360_OU_TOP: "360 OU Sup",
            VRGLWidget.STEREO_360_OU_BOTTOM: "360 OU Inf",
            VRGLWidget.STEREO_360_OU_DUAL: "360 OU Dual",
            VRGLWidget.STEREO_360_OU_INVERTED: "360 OU Invert",
        }
        btn_txt = names.get(mode_id, '3D')
        if (mode_id in [VRGLWidget.STEREO_VR180_SBS_LEFT, VRGLWidget.STEREO_VR180_SBS_RIGHT, VRGLWidget.STEREO_VR180_SBS_DUAL, VRGLWidget.STEREO_VR180_SBS_INVERTED]) and cur_dome == 190:
            btn_txt = btn_txt.replace("180", "190")
        self.btn_stereo_menu.setText(f"🕶️ {btn_txt} ▾")
        self._update_hud()

    def _on_speed_selected(self, speed_str):
        self.btn_speed_menu.setText(f"⚡ {speed_str} ▾")
        try:
            val = float(speed_str.replace("x", ""))
            self.backend.set_speed(val)
        except Exception:
            pass

    def _set_loop_state(self, enabled):
        self.btn_loop.setChecked(enabled)
        self.act_loop.setChecked(enabled)
        self.backend.set_loop(enabled)

    def _toggle_mute(self):
        if self.is_muted:
            self.is_muted = False
            self.vol_slider.setValue(self.pre_mute_volume)
            self.backend.set_volume(self.pre_mute_volume)
            self.btn_volume.setText("🔊")
        else:
            self.is_muted = True
            self.pre_mute_volume = self.vol_slider.value()
            self.vol_slider.setValue(0)
            self.backend.set_volume(0)
            self.btn_volume.setText("🔇")

    def _on_volume_changed(self, val):
        self.vol_slider.setToolTip(f"Volumen: {val}%")
        if val == 0:
            self.btn_volume.setText("🔇")
            self.is_muted = True
        else:
            self.is_muted = False
            if val < 40:
                self.btn_volume.setText("🔈")
            elif val < 75:
                self.btn_volume.setText("🔉")
            else:
                self.btn_volume.setText("🔊")
        self.backend.set_volume(val)

    def _connect_signals(self):
        self.backend.time_changed.connect(self._on_time_changed)
        self.backend.duration_changed.connect(self._on_duration_changed)
        self.backend.playback_state_changed.connect(self._on_playback_state_changed)
        self.backend.file_loaded.connect(self._on_file_loaded)
        self.backend.stats_updated.connect(self._on_stats_updated)
        self.viewport.camera_changed.connect(self._on_camera_changed)

    def _setup_shortcuts(self):
        # NOTA: Los atajos P, R, H, I, F, Espacio, Flechas Izq/Der y 1-5 están vinculados
        # directamente a sus respectivas QActions añadidas a la ventana principal.
        # Aquí solo configuramos atajos auxiliares que no tienen QAction en menú
        # para evitar el error 'Ambiguous shortcut overload'.
        QShortcut(QKeySequence(Qt.Key_F11), self, self._toggle_fullscreen)
        QShortcut(QKeySequence(Qt.Key_Escape), self, self._exit_fullscreen_only)
        QShortcut(QKeySequence(Qt.Key_Up), self, self._volume_up)
        QShortcut(QKeySequence(Qt.Key_Down), self, self._volume_down)
        QShortcut(QKeySequence(Qt.Key_M), self, self._toggle_mute)
        # Atajos de teclado para Zoom / FOV
        QShortcut(QKeySequence(Qt.Key_Plus), self, lambda: self.viewport.zoom_in(5.0))
        QShortcut(QKeySequence("="), self, lambda: self.viewport.zoom_in(5.0))
        QShortcut(QKeySequence(Qt.Key_Minus), self, lambda: self.viewport.zoom_out(5.0))
        QShortcut(QKeySequence("_"), self, lambda: self.viewport.zoom_out(5.0))
        QShortcut(QKeySequence(Qt.Key_0), self, self.viewport.reset_fov)

    def _volume_up(self):
        self.vol_slider.setValue(min(100, self.vol_slider.value() + 5))

    def _volume_down(self):
        self.vol_slider.setValue(max(0, self.vol_slider.value() - 5))

    def _toggle_hud(self):
        vis = not self.hud_pill.isVisible()
        self.hud_pill.setVisible(vis)
        self.btn_hud_btn.setChecked(vis)
        self.act_hud_toggle.setChecked(vis)

    # Inversión de Ejes Separada con Guardado Persistente en QSettings
    def _toggle_invert_x(self, checked=None):
        if checked is None:
            checked = not self.viewport.invert_x
        self.viewport.set_invert_x(checked)
        self.settings.setValue("invert_x", bool(checked))
        self.settings.sync()
        self._sync_invert_ui()

    def _toggle_invert_y(self, checked=None):
        if checked is None:
            checked = not self.viewport.invert_y
        self.viewport.set_invert_y(checked)
        self.settings.setValue("invert_y", bool(checked))
        self.settings.sync()
        self._sync_invert_ui()

    def _toggle_invert_both(self):
        new_val = not (self.viewport.invert_x and self.viewport.invert_y)
        self.viewport.set_invert_x(new_val)
        self.viewport.set_invert_y(new_val)
        self.settings.setValue("invert_x", new_val)
        self.settings.setValue("invert_y", new_val)
        self.settings.sync()
        self._sync_invert_ui()

    def _sync_invert_ui(self):
        inv_x = self.viewport.invert_x
        inv_y = self.viewport.invert_y

        self.act_inv_x.setChecked(inv_x)
        self.act_inv_y.setChecked(inv_y)

        any_inv = inv_x or inv_y
        self.btn_invert_axes.setChecked(any_inv)

        str_h = "Sí" if inv_x else "No"
        str_v = "Sí" if inv_y else "No"
        self.btn_invert_axes.setToolTip(f"Inversión de ejes (I) [Horizontal: {str_h} | Vertical: {str_v}]")

    def _toggle_flip_x(self, flipped=None):
        if flipped is None:
            flipped = not (self.viewport.flip_x == 1)
        self.viewport.flip_x = 1 if flipped else 0
        self.settings.setValue("flip_x", bool(self.viewport.flip_x))
        self.settings.sync()
        self._sync_flip_ui()
        self.viewport.update()

    def _toggle_flip_y(self, flipped=None):
        if flipped is None:
            flipped = not (self.viewport.flip_y == 1)
        self.viewport.flip_y = 1 if flipped else 0
        self.settings.setValue("flip_y", bool(self.viewport.flip_y))
        self.settings.sync()
        self._sync_flip_ui()
        self.viewport.update()

    def _sync_flip_ui(self):
        fx = bool(self.viewport.flip_x)
        fy = bool(self.viewport.flip_y)
        if hasattr(self, 'btn_flip_x_btn'):
            self.btn_flip_x_btn.setChecked(fx)
        if hasattr(self, 'act_flip_x'):
            self.act_flip_x.setChecked(fx)
        if hasattr(self, 'btn_flip_btn'):
            self.btn_flip_btn.setChecked(fy)
        if hasattr(self, 'act_flip_y'):
            self.act_flip_y.setChecked(fy)

    def _toggle_auto_orbit(self, checked=None):
        if checked is None:
            checked = not self.viewport.auto_orbit
        self.viewport.auto_orbit = bool(checked)
        self.btn_orbit.setChecked(bool(checked))
        self.act_orbit.setChecked(bool(checked))

    def _toggle_fullscreen(self):
        if self.isFullScreen():
            self.menuBar().setVisible(True)
            self.btn_fullscreen.setText("⛶")
            if getattr(self, '_was_maximized', False):
                self.showMaximized()
            else:
                self.showNormal()

            # Garantizar que el botón de cerrar ('X') de Windows permanezca activo
            try:
                import ctypes
                hwnd = int(self.winId())
                ctypes.windll.user32.GetSystemMenu(hwnd, True)
                hmenu = ctypes.windll.user32.GetSystemMenu(hwnd, False)
                if hmenu:
                    ctypes.windll.user32.EnableMenuItem(hmenu, 0xF060, 0x00000000)
            except Exception:
                pass
        else:
            self._was_maximized = self.isMaximized()
            self.menuBar().setVisible(False)
            self.btn_fullscreen.setText("🗗")
            self.showFullScreen()

        self._reposition_overlays()
        self.viewport.update()

    def _exit_fullscreen_only(self):
        if self.isFullScreen():
            self._toggle_fullscreen()

    def keyPressEvent(self, event):
        # Fallback de atajos directos en la ventana para garantizar respuesta inmediata
        key = event.key()
        if key == Qt.Key_Escape:
            if hasattr(self, 'overlay_menu') and self.overlay_menu.isVisible():
                self.overlay_menu.hide()
                event.accept()
                return
            if self.isFullScreen():
                self._toggle_fullscreen()
                event.accept()
                return
        elif key in (Qt.Key_F, Qt.Key_F11):
            self._toggle_fullscreen()
            event.accept()
            return
        elif key == Qt.Key_Space:
            self.backend.toggle_play()
            event.accept()
            return
        elif key == Qt.Key_P:
            self._cycle_next_projection()
            event.accept()
            return
        elif key == Qt.Key_H:
            self._toggle_hud()
            event.accept()
            return
        elif key == Qt.Key_I:
            self._toggle_invert_both()
            event.accept()
            return
        elif key == Qt.Key_R:
            self.viewport.recenter_view()
            event.accept()
            return
        elif key == Qt.Key_E:
            self._toggle_stereo_eye()
            event.accept()
            return
        super().keyPressEvent(event)

    def _install_tooltip_filter(self, parent_widget):
        parent_widget.installEventFilter(self)
        for child in parent_widget.findChildren(QWidget):
            child.installEventFilter(self)

    def eventFilter(self, watched, event):
        etype = event.type()
        if etype == QEvent.ToolTip:
            # Si el overlay de menú está visible, suprimir tooltips
            if hasattr(self, 'overlay_menu') and self.overlay_menu.isVisible():
                return True
            tip_text = watched.toolTip() if hasattr(watched, 'toolTip') else ""
            if tip_text and hasattr(self, 'in_viewport_tooltip'):
                self.in_viewport_tooltip.show_tip(tip_text, watched)
                return True  # Evita que Windows/Qt lance el QToolTip nativo (WS_POPUP invisible en pantalla completa)
        elif etype in (QEvent.Leave, QEvent.MouseButtonPress, QEvent.Hide):
            if hasattr(self, 'in_viewport_tooltip') and self.in_viewport_tooltip.isVisible():
                self.in_viewport_tooltip.hide_tip()
        return super().eventFilter(watched, event)

    def changeEvent(self, event):
        super().changeEvent(event)
        if event.type() == QEvent.WindowStateChange:
            is_fs = self.isFullScreen()
            self.menuBar().setVisible(not is_fs)
            if hasattr(self, 'btn_fullscreen'):
                self.btn_fullscreen.setText("🗗" if is_fs else "⛶")
            self._reposition_overlays()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._reposition_overlays()

    def _reposition_overlays(self):
        w = self.viewport.width()
        h = self.viewport.height()
        if w <= 0 or h <= 0:
            return

        # 1. Reposicionar barra inferior flotante
        margin = 16
        bar_height = 86
        bar_width = min(w - 2 * margin, 1260)
        bar_x = (w - bar_width) // 2
        bar_y = h - bar_height - margin
        self.bottom_bar.setGeometry(bar_x, bar_y, bar_width, bar_height)
        self.bottom_bar.raise_()

        # 2. Reposicionar HUD Pill en esquina superior izquierda
        self.hud_pill.setGeometry(16, 16, self.hud_pill.sizeHint().width() + 10, self.hud_pill.sizeHint().height())
        self.hud_pill.raise_()

        # 3. Reposicionar Welcome Card centrada
        card_w = min(w - 40, 560)
        card_h = self.welcome_card.sizeHint().height()
        card_x = (w - card_w) // 2
        card_y = (h - card_h) // 2 - 20
        self.welcome_card.setGeometry(card_x, card_y, card_w, card_h)
        self.welcome_card.raise_()

        # 4. Reposicionar overlay_menu si está visible
        if hasattr(self, 'overlay_menu') and self.overlay_menu.isVisible():
            self.overlay_menu._refit_geometry()
            self.overlay_menu.raise_()

        # 5. Ocultar tooltip al redimensionar para evitar desalineación
        if hasattr(self, 'in_viewport_tooltip') and self.in_viewport_tooltip.isVisible():
            self.in_viewport_tooltip.hide_tip()

    def _open_file_dialog(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Abrir Video 360° / VR / 8K",
            base_dir,
            "Archivos de Video (*.mp4 *.mkv *.mov *.webm *.ts *.360 *.insv);;Todos los archivos (*.*)"
        )
        if path:
            self.load_video(path)

    def _open_url_dialog(self):
        url, ok = QInputDialog.getText(self, "Abrir URL de Red", "Introduzca enlace RTSP / HTTP / HLS:")
        if ok and url:
            self.load_video(url)

    def _load_demo_8k(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        demo_path = os.path.join(base_dir, "test_vr360_8k.mp4")
        if os.path.exists(demo_path):
            self.load_video(demo_path)

    def _load_demo_180(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        demo_path = os.path.join(base_dir, "test_vr180_sbs.mp4")
        if os.path.exists(demo_path):
            self.load_video(demo_path)

    def _load_demo_190(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        demo_path = os.path.join(base_dir, "test_vr190_sbs.mp4")
        if os.path.exists(demo_path):
            self.load_video(demo_path)


    def load_video(self, path):
        success = self.backend.load_file(path)
        if success:
            self.welcome_card.setVisible(False)
            base_name = os.path.basename(path)
            self.setWindowTitle(f"OmniVR Player 8K — {base_name}")

            # Auto-detección inteligente por patrones de nombre de archivo personalizables
            matched_rule = self.pattern_manager.match(base_name)
            if matched_rule:
                st = matched_rule.get("stereo", "MONO")
                dome_fov = float(matched_rule.get("dome_fov", 180.0))
                lens_model = int(matched_rule.get("lens_model", 0))
                proj_mode = matched_rule.get("projection", "RECTILINEAR")

                stereo_map = {
                    "MONO": VRGLWidget.STEREO_MONO,
                    "VR180_SBS": VRGLWidget.STEREO_VR180_SBS_LEFT,
                    "VR180_SBS_RIGHT": VRGLWidget.STEREO_VR180_SBS_RIGHT,
                    "VR190_SBS": VRGLWidget.STEREO_VR180_SBS_LEFT,
                    "VR190_SBS_RIGHT": VRGLWidget.STEREO_VR180_SBS_RIGHT,
                    "360_SBS": VRGLWidget.STEREO_360_SBS_LEFT,
                    "360_SBS_RIGHT": VRGLWidget.STEREO_360_SBS_RIGHT,
                    "360_OU": VRGLWidget.STEREO_360_OU_TOP,
                    "360_OU_BOTTOM": VRGLWidget.STEREO_360_OU_BOTTOM,
                    "DUAL_VR180": VRGLWidget.STEREO_VR180_SBS_DUAL,
                    "DUAL_360_SBS": VRGLWidget.STEREO_360_SBS_DUAL,
                    "DUAL_360_OU": VRGLWidget.STEREO_360_OU_DUAL,
                }
                mode_id = stereo_map.get(st, VRGLWidget.STEREO_MONO)

                # Si es modo domo hemisférico (VR180 / VR190 SBS)
                if mode_id in [VRGLWidget.STEREO_VR180_SBS_LEFT, VRGLWidget.STEREO_VR180_SBS_RIGHT]:
                    self._set_dome_fov(dome_fov)
                    self._set_lens_model(lens_model)
                elif mode_id in [VRGLWidget.STEREO_360_SBS_LEFT, VRGLWidget.STEREO_360_SBS_RIGHT, VRGLWidget.STEREO_360_OU_TOP, VRGLWidget.STEREO_360_OU_BOTTOM]:
                    self._set_dome_fov(180.0)
                    self._set_lens_model(0)

                self._set_stereo_mode(mode_id)

                proj_map = {
                    "RECTILINEAR": VRGLWidget.PROJ_RECTILINEAR,
                    "LITTLE_PLANET": VRGLWidget.PROJ_LITTLE_PLANET,
                    "FISHEYE": VRGLWidget.PROJ_FISHEYE,
                    "PANINI": VRGLWidget.PROJ_PANINI,
                    "SPHERICAL_360": VRGLWidget.PROJ_SPHERICAL_360,
                }
                if proj_mode in proj_map:
                    self._set_projection_mode(proj_map[proj_mode])

                print(f"[OmniVR] Auto-detección aplicada: Regla '{matched_rule.get('name')}' para '{base_name}'")
            else:
                self._set_stereo_mode(VRGLWidget.STEREO_MONO)

            self._wake_ui()

    def _on_time_changed(self, t):
        dur = self.backend.duration
        if not self.seek_slider.isSliderDown() and dur > 0:
            val = int((t / dur) * 1000)
            self.seek_slider.setValue(val)
        self.cur_time_label.setText(self._fmt_time(t))

    def _on_duration_changed(self, dur):
        self.seek_slider.set_duration(dur)
        self.total_time_label.setText(self._fmt_time(dur))

    def _fmt_time(self, s):
        s = max(0, int(s))
        m, s = divmod(s, 60)
        h, m = divmod(m, 60)
        return f"{h:02d}:{m:02d}:{s:02d}"

    def _on_playback_state_changed(self, is_playing):
        self.btn_play.setText("⏸" if is_playing else "▶")
        self.act_play_pause.setText("⏸ Pausar" if is_playing else "▶ Reproducir")

    def _on_seek_moved(self, val):
        dur = self.backend.duration
        if dur > 0:
            target = (val / 1000.0) * dur
            self.cur_time_label.setText(self._fmt_time(target))

    def _on_seek_released(self):
        val = self.seek_slider.value()
        dur = self.backend.duration
        if dur > 0:
            self.backend.seek((val / 1000.0) * dur, absolute=True)

    def _on_seek_clicked(self, val):
        dur = self.backend.duration
        if dur > 0:
            self.backend.seek((val / 1000.0) * dur, absolute=True)

    def _on_file_loaded(self, info):
        w = info.get('width', 0)
        h = info.get('height', 0)
        codec = info.get('codec', '')
        hwdec = info.get('hwdec', 'd3d11va')

        res_str = f"{w}x{h}"
        if w >= 7000:
            res_str += " (8K)"
        elif w >= 3800:
            res_str += " (4K)"

        self.badge_label.setText(f"⚡ {str(hwdec).upper()} [{res_str}]")
        self._update_hud()

    def _on_stats_updated(self, stats):
        self._update_hud(stats)

    def _on_camera_changed(self, yaw, pitch, roll, fov):
        if hasattr(self, 'btn_fov'):
            self.btn_fov.setText(f"🔍 {int(round(fov))}° ▾")
        self._update_hud()

    def _update_hud(self, stats=None):
        if not self.hud_pill.isVisible():
            return

        w = self.backend.video_width
        h = self.backend.video_height
        codec = getattr(self.backend.mpv_player, 'video_codec', 'HEVC') if self.backend.mpv_player else 'HEVC'
        hwdec = getattr(self.backend.mpv_player, 'hwdec_current', 'd3d11va') if self.backend.mpv_player else 'd3d11va'
        fps = getattr(self.backend.mpv_player, 'estimated_vf_fps', 60.0) if self.backend.mpv_player else 60.0
        drops = getattr(self.backend.mpv_player, 'frame_drop_count', 0) if self.backend.mpv_player else 0
        if stats:
            fps = stats.get('fps', fps)
            drops = stats.get('drops', drops)
        fps = float(fps if fps is not None else 60.0)
        drops = int(drops if drops is not None else 0)

        res_str = f"{w}x{h}" if w > 0 else "Sin video"
        if w >= 7000:
            res_str += " <b style='color:#38bdf8;'>[8K UHD]</b>"

        proj_names = {
            VRGLWidget.PROJ_RECTILINEAR: "Rectilíneo",
            VRGLWidget.PROJ_LITTLE_PLANET: "Little Planet",
            VRGLWidget.PROJ_FISHEYE: "Ojo de Pez",
            VRGLWidget.PROJ_PANINI: "Panini",
            VRGLWidget.PROJ_SPHERICAL_360: "360° Esférico"
        }
        proj_str = proj_names.get(self.viewport.projection_mode, "Rectilíneo")

        stereo_names = {
            VRGLWidget.STEREO_MONO: "Mono 2D",
            VRGLWidget.STEREO_VR180_SBS_LEFT: "VR180 SBS (Izq)",
            VRGLWidget.STEREO_VR180_SBS_RIGHT: "VR180 SBS (Der)",
            VRGLWidget.STEREO_VR180_SBS_DUAL: "VR180 Dual HMD",
            VRGLWidget.STEREO_VR180_SBS_INVERTED: "VR180 Invertido",
            VRGLWidget.STEREO_360_SBS_LEFT: "360 SBS (Izq)",
            VRGLWidget.STEREO_360_SBS_RIGHT: "360 SBS (Der)",
            VRGLWidget.STEREO_360_SBS_DUAL: "360 SBS Dual",
            VRGLWidget.STEREO_360_SBS_INVERTED: "360 Invertido",
            VRGLWidget.STEREO_360_OU_TOP: "360 OU (Sup)",
            VRGLWidget.STEREO_360_OU_BOTTOM: "360 OU (Inf)",
            VRGLWidget.STEREO_360_OU_DUAL: "360 OU Dual",
            VRGLWidget.STEREO_360_OU_INVERTED: "360 OU Invertido",
        }
        stereo_str = stereo_names.get(self.viewport.stereo_mode, "Mono 2D")
        lens_info = " [Canon Fisheye]" if self.viewport.get_lens_model() == 1 else ""
        dome_deg = self.viewport.get_dome_fov_degrees()
        dome_info = f" | Domo: {dome_deg:.0f}°{lens_info}" if (self.viewport.stereo_mode >= 1 and self.viewport.stereo_mode <= 4) else ""
        hud_text = (
            f"<b>OmniVR 8K Player</b> — <i>GPU {str(hwdec).upper()} [RTX 5090]</i><br>"
            f"<b>Resolución:</b> {res_str} | <b>Códec:</b> {codec}<br>"
            f"<b>FPS:</b> {fps:.1f} | <b>Pérdida cuadros:</b> {drops}<br>"
            f"<b>Orientación:</b> Yaw: {math.degrees(self.viewport.yaw):+06.1f}° | "
            f"Pitch: {math.degrees(self.viewport.pitch):+05.1f}° | "
            f"FOV: {math.degrees(self.viewport.fov):.1f}°{dome_info}<br>"
            f"<b>Proyección:</b> {proj_str} | <b>Modo 3D:</b> {stereo_str}"
        )
        self.hud_label.setText(hud_text)
        self.hud_pill.adjustSize()

    # Interacción de ratón y auto-ocultación inteligente (GoPro VR Player style)
    def _wake_ui(self):
        if not self.is_ui_visible:
            self.bottom_bar.setVisible(True)
            self.is_ui_visible = True
        self.hide_timer.start()

    def _handle_mouse_move_hover(self, mouse_y):
        """Maneja la visibilidad de la barra inferior según la posición Y del cursor."""
        # Si el usuario está rotando la cámara 360°, no activar la barra para no estorbar
        if getattr(self.viewport, 'is_dragging_left', False) or getattr(self.viewport, 'is_dragging_right', False):
            return

        h = self.viewport.height()
        bottom_threshold = max(0, h - 130)

        # La barra solo debe salir si el mouse se posiciona en la parte de abajo
        is_in_bottom_zone = (mouse_y >= bottom_threshold) or self.bottom_bar.underMouse()

        if is_in_bottom_zone:
            if not self.bottom_bar.isVisible():
                self.bottom_bar.setVisible(True)
                self.is_ui_visible = True
            self.hide_timer.start()
        else:
            # Si el ratón sale de la zona inferior y no hay menú abierto, ocultar la barra
            if self.backend.current_file and not self._is_any_menu_active():
                if self.bottom_bar.isVisible():
                    self.bottom_bar.setVisible(False)
                    self.is_ui_visible = False

    def _is_any_menu_active(self):
        """Comprueba si el menú flotante in-viewport está visible."""
        if hasattr(self, 'overlay_menu') and self.overlay_menu.isVisible():
            return True
        return False

    def _auto_hide_ui(self):
        # No ocultar la barra si hay un menú abierto o si el cursor está sobre la barra
        if self._is_any_menu_active():
            self.hide_timer.start()
            return
        if self.bottom_bar.underMouse():
            self.hide_timer.start()
            return
        if self.backend.current_file:
            self.bottom_bar.setVisible(False)
            self.is_ui_visible = False

    def show_context_menu(self, pos=None):
        """
        Menú contextual con clic derecho renderizado con VROverlayMenu dentro del viewport OpenGL.
        100% visible tanto en ventana normal como en pantalla completa (inmune a NVIDIA DirectFlip).
        """
        if isinstance(pos, QPoint):
            target_pos = pos
        elif isinstance(pos, QPointF):
            target_pos = pos.toPoint()
        else:
            target_pos = self.viewport.mapFromGlobal(QCursor.pos())

        self.overlay_menu.show_builder(self._build_context_menu, anchor_pos=target_pos)

    def _show_shortcuts_dialog(self):
        """Muestra el diálogo de atajos de teclado y controles con estética Glassmorphic de alto contraste."""
        dlg = VRShortcutsDialog(self)
        dlg.exec()

    def _show_about_dialog(self):
        """Muestra la ventana Acerca de OmniVR Player 8K con diseño moderno y legible."""
        dlg = VRAboutDialog(self)
        dlg.exec()

    def _show_patterns_dialog(self):
        """Muestra el configurador de patrones de nombres de archivo con probador en tiempo real."""
        cur_file = os.path.basename(self.backend.current_file) if getattr(self.backend, 'current_file', None) else ""
        dlg = VRFilenamePatternsDialog(self.pattern_manager, sample_filename=cur_file, parent=self)
        if dlg.exec() == QDialog.Accepted and cur_file:
            # Re-aplicar auto-detección al video actualmente cargado si existe
            matched = self.pattern_manager.match(cur_file)
            if matched:
                st = matched.get("stereo", "MONO")
                dome_fov = float(matched.get("dome_fov", 180.0))
                lens_model = int(matched.get("lens_model", 0))
                proj_mode = matched.get("projection", "RECTILINEAR")

                stereo_map = {
                    "MONO": VRGLWidget.STEREO_MONO,
                    "VR180_SBS": VRGLWidget.STEREO_VR180_SBS_LEFT,
                    "VR180_SBS_RIGHT": VRGLWidget.STEREO_VR180_SBS_RIGHT,
                    "VR190_SBS": VRGLWidget.STEREO_VR180_SBS_LEFT,
                    "VR190_SBS_RIGHT": VRGLWidget.STEREO_VR180_SBS_RIGHT,
                    "360_SBS": VRGLWidget.STEREO_360_SBS_LEFT,
                    "360_SBS_RIGHT": VRGLWidget.STEREO_360_SBS_RIGHT,
                    "360_OU": VRGLWidget.STEREO_360_OU_TOP,
                    "360_OU_BOTTOM": VRGLWidget.STEREO_360_OU_BOTTOM,
                    "DUAL_VR180": VRGLWidget.STEREO_VR180_SBS_DUAL,
                    "DUAL_360_SBS": VRGLWidget.STEREO_360_SBS_DUAL,
                    "DUAL_360_OU": VRGLWidget.STEREO_360_OU_DUAL,
                }
                mode_id = stereo_map.get(st, VRGLWidget.STEREO_MONO)
                if mode_id in [VRGLWidget.STEREO_VR180_SBS_LEFT, VRGLWidget.STEREO_VR180_SBS_RIGHT]:
                    self._set_dome_fov(dome_fov)
                    self._set_lens_model(lens_model)
                elif mode_id in [VRGLWidget.STEREO_360_SBS_LEFT, VRGLWidget.STEREO_360_SBS_RIGHT, VRGLWidget.STEREO_360_OU_TOP, VRGLWidget.STEREO_360_OU_BOTTOM]:
                    self._set_dome_fov(180.0)
                    self._set_lens_model(0)
                self._set_stereo_mode(mode_id)

                proj_map = {
                    "RECTILINEAR": VRGLWidget.PROJ_RECTILINEAR,
                    "LITTLE_PLANET": VRGLWidget.PROJ_LITTLE_PLANET,
                    "FISHEYE": VRGLWidget.PROJ_FISHEYE,
                    "PANINI": VRGLWidget.PROJ_PANINI,
                    "SPHERICAL_360": VRGLWidget.PROJ_SPHERICAL_360,
                }
                if proj_mode in proj_map:
                    self._set_projection_mode(proj_map[proj_mode])


    # Drag & Drop handling
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        if urls:
            filepath = urls[0].toLocalFile()
            if os.path.exists(filepath):
                self.load_video(filepath)

    def closeEvent(self, event):
        self.hide_timer.stop()
        self.viewport.cleanup()
        self.backend.cleanup()
        super().closeEvent(event)
