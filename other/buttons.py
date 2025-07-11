from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


class Button(QFrame):

    clicked = Signal()

    def __init__(self, text: str = "", icon: QIcon = None, *args, **kwargs):
        super().__init__(*args, *kwargs)

        # self.setFixedSize(250, 50)
        self.text_color = "white"
        self.set_stylesheet("#303030")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setObjectName("main-frame")

        self.label_text = text
        self.button_icon = icon

        self.smaller_font_size = 18
        self.larger_font_size = 20
        self.main_font = QFont("Jetbrains Mono", self.larger_font_size)

        self.main_layout = QHBoxLayout(self)
        self.setLayout(self.main_layout)
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        self.main_layout.setSpacing(5)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.label = None
        if self.label_text:
            self.label = QLabel(self.label_text)
            self.label.setFont(self.main_font)
            self.main_layout.addWidget(self.label)

        self.icon_button = None
        self.smaller_button_icon_size = 36
        self.larger_button_icon_size = 40
        if self.button_icon:
            self.icon_button = QPushButton("")
            self.icon_button.setIcon(self.button_icon)
            self.icon_button.setIconSize(
                QSize(self.larger_button_icon_size, self.larger_button_icon_size)
            )
            self.icon_button.setStyleSheet("border: none;")

            # to make sure that clicking on the actual button (the icon) itself
            # still behaves properly
            self.icon_button.mousePressEvent = self.mousePressEvent
            self.main_layout.insertWidget(0, self.icon_button)

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

    def set_font_sizes(self, smaller: int, larger: int) -> None:
        self.smaller_font_size = smaller
        self.larger_font_size = larger
        self.main_font = QFont("Jetbrains Mono", self.larger_font_size)
        self.label.setFont(self.main_font)

    def set_icon_sizes(self, smaller: int, larger: int) -> None:
        self.smaller_button_icon_size = smaller
        self.larger_button_icon_size = larger
        self.icon_button.setIconSize(QSize(larger, larger))

    def mousePressEvent(self, event: QMouseEvent, /) -> None:
        if self.label:
            self.main_font.setPointSize(self.smaller_font_size)
            self.label.setFont(self.main_font)

        if self.icon_button:
            self.icon_button.setIconSize(
                QSize(self.smaller_button_icon_size, self.smaller_button_icon_size)
            )
        return super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent, /) -> None:
        if self.label:
            self.main_font.setPointSize(self.larger_font_size)
            self.label.setFont(self.main_font)

        if self.rect().contains(event.pos()):
            self.clicked.emit()

        if self.icon_button:
            self.icon_button.setIconSize(
                QSize(self.larger_button_icon_size, self.larger_button_icon_size)
            )
        return super().mouseReleaseEvent(event)

    def enterEvent(self, event: QEnterEvent, /) -> None:
        self.set_stylesheet("#404040")
        return super().enterEvent(event)

    def leaveEvent(self, event: QEvent, /) -> None:
        self.set_stylesheet("#303030")
        return super().leaveEvent(event)

    def doubleClickEvent(self, event: QMouseEvent, /) -> None:
        event.ignore()
