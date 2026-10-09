"""
OmniVR Player 8K — Reproductor de Video VR para Windows
Inspirado en GoPro VR Player 3.0.5 con aceleración por GPU (NVIDIA RTX / D3D11VA / NVDEC).
"""

import os
import sys

# Ensure DLL path for libmpv-2.dll
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if hasattr(os, 'add_dll_directory'):
    os.add_dll_directory(BASE_DIR)
os.environ['PATH'] = BASE_DIR + os.pathsep + os.environ.get('PATH', '')

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

from ui_main_window import VRMainWindow


def main():
    # Enable High-DPI support
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("OmniVR Player 8K")
    app.setOrganizationName("OmniVR")

    video_to_load = None
    if len(sys.argv) > 1 and os.path.isfile(sys.argv[1]):
        video_to_load = sys.argv[1]

    window = VRMainWindow(initial_video=video_to_load)
    window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
