from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from other.buttons import Button


class SideBar(QFrame):

    clicked = Signal(str)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, *kwargs)

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.setObjectName("side-bar")
        self.setStyleSheet(
            """
            #side-bar{
                border-radius: 0px;
                border-top-left-radius: 5px;
                border-bottom-left-radius: 5px;
            }
            QFrame{
                background-color: #303030;
                color: white;
            }
            """
        )

        self.main_layout = QVBoxLayout(self)
        self.setLayout(self.main_layout)
        self.main_layout.setContentsMargins(15, 15, 15, 15)
        self.main_layout.setSpacing(15)
        self.main_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter
        )

        self.confirm_button = Button("Save", QIcon("assets/check.svg"))
        self.delete_button = Button("Delete", QIcon("assets/delete.svg"))
        self.search_button = Button("Search", QIcon("assets/search.svg"))
        self.refresh_button = Button("Refresh", QIcon("assets/refresh.svg"))

        for button in [
            self.confirm_button,
            self.delete_button,
            self.search_button,
            self.refresh_button,
        ]:
            button.clicked.connect(
                lambda b=button: self.clicked.emit(b.label_text.lower())
            )
            self.main_layout.addWidget(button)
