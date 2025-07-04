from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


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

        self.confirm_button = IconButton("Save", QIcon("assets/check.svg"))
        self.delete_button = IconButton("Delete", QIcon("assets/delete.svg"))
        self.search_button = IconButton("Search", QIcon("assets/search.svg"))
        self.refresh_button = IconButton("Refresh", QIcon("assets/refresh.svg"))

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


class IconButton(QFrame):

    clicked = Signal()

    def __init__(self, text: str, icon: QIcon, *args, **kwargs):
        super().__init__(*args, *kwargs)

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setFixedHeight(50)
        self.set_stylesheet("#303030")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setObjectName("main-frame")

        self.label_text = text
        self.button_icon = icon

        self.main_layout = QHBoxLayout(self)
        self.setLayout(self.main_layout)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(5)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.main_font = QFont("Jetbrains Mono", 20)
        self.label = QLabel(self.label_text)
        self.label.setFont(self.main_font)

        self.icon_button = QPushButton("")
        self.icon_button.setIcon(self.button_icon)
        self.icon_button.setIconSize(QSize(40, 40))

        # make sure that if you click on the button specifically,
        # it will click the entire thing
        self.icon_button.mousePressEvent = self.mousePressEvent

        self.icon_button.setStyleSheet(
            """
            border: none;
            """
        )

        self.main_layout.addWidget(self.icon_button)
        self.main_layout.addWidget(self.label)

    def set_stylesheet(self, color: str) -> None:
        self.setStyleSheet(
            f"""
            *{{
                background-color: {color};
                color: white;
                border-radius: 5px;
            }}
            #main-frame {{
                border: 1px solid hsla(0, 0%, 90%, 10%)
            }}
            """
        )

    def mousePressEvent(self, event: QMouseEvent, /) -> None:
        self.main_font.setPointSize(18)
        self.label.setFont(self.main_font)

        self.icon_button.setIconSize(QSize(35, 35))
        return super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent, /) -> None:
        self.main_font.setPointSize(20)
        self.clicked.emit()
        self.label.setFont(self.main_font)

        self.icon_button.setIconSize(QSize(40, 40))
        return super().mouseReleaseEvent(event)

    def enterEvent(self, event: QEnterEvent, /) -> None:
        self.set_stylesheet("#404040")
        return super().enterEvent(event)

    def leaveEvent(self, event: QEvent, /) -> None:
        self.set_stylesheet("#303030")
        return super().leaveEvent(event)
