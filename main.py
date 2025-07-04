from rich.traceback import install
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
import qdarktheme
import sys
from AsyncioPySide6 import AsyncioPySide6

from widgets.interface import Interface

install()


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, *kwargs)

        self.setFixedSize(1920, 1080)

        self.main_widget = QFrame(self)
        self.main_layout = QVBoxLayout(self.main_widget)
        self.main_widget.setLayout(self.main_layout)

        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.main_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter
        )

        self.interface = Interface()
        self.main_layout.addWidget(self.interface)

        self.setCentralWidget(self.main_widget)

    def keyPressEvent(self, event: QKeyEvent, /) -> None:
        if event.key() == Qt.Key.Key_Escape:
            self.close()

        return super().keyPressEvent(event)


app = QApplication(sys.argv)
qdarktheme.load_stylesheet()
with AsyncioPySide6.use_asyncio():
    main_window = MainWindow()
    main_window.show()
    app.exec()
