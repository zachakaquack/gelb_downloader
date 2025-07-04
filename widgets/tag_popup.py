from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
import re

from other import file_management


def parse(text: str, gelb_ready=False) -> list:
    """
    all tags can be separated by spaces; aside from tags within {}, or
    the OR search.
    finds the OR brackets and parses them.
    """
    text = re.sub(r"\s+", " ", text.strip())

    def normalize_brace(match):
        inner = match.group(1)
        if gelb_ready:
            normalized = re.sub(r"\s*~\s*", "+~+", inner)
        else:
            normalized = re.sub(r"\s*~\s*", " ~ ", inner)

        normalized = re.sub(r"\s+", " ", normalized).strip()
        return f"{{{normalized}}}"

    text = re.sub(r"\{(.*?)\}", normalize_brace, text)

    tags = []
    buffer = ""
    in_brace = False

    for part in text.split(" "):
        if in_brace:
            buffer += " " + part
            if "}" in part:
                in_brace = False

                if gelb_ready:
                    tags.append(buffer.strip())
                else:
                    tags.append(buffer[1:-1].strip())

                buffer = ""

        elif part.startswith("{") and not part.endswith("}"):
            buffer = part
            in_brace = True

        elif part.startswith("{") and part.endswith("}"):
            if gelb_ready:
                tags.append(part.strip())
            else:
                tags.append(part[1:-1].strip())

        else:
            tags.append(part.strip())

    return tags


class TagPopup(QFrame):

    search = Signal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, *kwargs)

        self.setFixedHeight(500)
        self.setWindowTitle("TagPopupFloating")
        self.setWindowFlags(
            Qt.WindowType.Popup
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMinimumWidth(1000)

        self.setStyleSheet(
            """
            background-color: #1e1e1e;
            color: white;
            """
        )

        self.main_layout = QVBoxLayout(self)
        self.setLayout(self.main_layout)
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        self.main_layout.setSpacing(5)
        self.main_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter
        )

        # help bar
        self.help_button = QPushButton("", self)
        self.help_button.setStyleSheet("""border:none;""")
        self.help_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.help_button.setIcon(QIcon("./assets/help.svg"))
        self.help_button.setIconSize(QSize(20, 20))

        self.main_layout.addWidget(
            self.help_button, stretch=1, alignment=Qt.AlignmentFlag.AlignRight
        )

        self.content_area = TagContentArea()
        self.main_layout.addWidget(self.content_area)

        self.buttons = Buttons()
        self.main_layout.addWidget(self.buttons)

        self.buttons.cancel.connect(self.close)
        self.buttons.search.connect(self.prepare_search)

    def prepare_search(self) -> None:

        text = self.content_area.search_and_history.search_bar.text()
        text = parse(text, gelb_ready=True)

        limit = self.content_area.search_and_history.limit_spin.value()

        # so stupid lmfao
        random = not self.content_area.search_and_history.random_button.isChecked()

        file_management.save_search(text, limit, random)

        self.search.emit()


class Buttons(QFrame):

    cancel = Signal()
    search = Signal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, *kwargs)

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.main_layout = QHBoxLayout(self)
        self.setLayout(self.main_layout)
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        self.main_layout.setSpacing(5)
        self.main_layout.setAlignment(
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight
        )

        self.cancel_button = IconButton("Cancel", QIcon("./assets/cancel.svg"))
        self.search_button = IconButton("Search", QIcon("./assets/search.svg"))

        self.main_layout.addWidget(self.cancel_button)
        self.main_layout.addWidget(self.search_button)

        self.cancel_button.clicked.connect(self.cancel.emit)
        self.search_button.clicked.connect(self.search.emit)


class TagContentArea(QFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, *kwargs)

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.main_layout = QHBoxLayout(self)
        self.setLayout(self.main_layout)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(10)
        self.main_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter
        )

        self.search_and_history = SearchAndHistory()
        self.tag_graph = TagGraph()

        self.search_and_history.searchTextChanged.connect(
            self.tag_graph.update_tag_graph
        )

        self.tag_graph.widgetRemoved.connect(self.search_and_history.remove_tag)

        self.main_layout.addWidget(self.search_and_history)
        self.main_layout.addWidget(self.tag_graph)

        self.main_layout.setStretch(10, 60)
        self.main_layout.setStretch(1, 40)


class SearchAndHistory(QFrame):

    searchTextChanged = Signal(str)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, *kwargs)

        self.setFixedWidth(500)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.main_layout = QVBoxLayout(self)
        self.setLayout(self.main_layout)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(5)
        self.main_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter
        )

        self.search_bar = QLineEdit(self)
        self.search_bar.setFixedHeight(50)
        self.search_bar.setFont(QFont("Jetbrains Mono", 16))
        self.search_bar.textChanged.connect(self.searchTextChanged.emit)
        self.search_bar.setStyleSheet(
            """
            background-color: #303030;
            border-radius: 5px;
            """
        )

        self.main_layout.addWidget(self.search_bar)

        self.limit_random_frame = QFrame(self)
        self.limit_random_layout = QHBoxLayout(self.limit_random_frame)
        self.limit_random_frame.setLayout(self.limit_random_layout)
        self.limit_random_layout.setContentsMargins(0, 0, 0, 0)
        self.limit_random_layout.setSpacing(10)
        self.limit_random_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout = QHBoxLayout()
        l = QLabel("Limit: ")
        l.setFont(QFont("Jetbrains Mono", 12))
        layout.addWidget(l)

        self.limit_spin = QSpinBox(self)
        self.limit_spin.setMinimum(0)
        self.limit_spin.setMaximum(100)
        self.limit_spin.setValue(10)

        self.random_button = self.RandomButton("Random")

        layout.addWidget(self.limit_spin)
        self.limit_random_layout.addLayout(layout)

        self.limit_random_layout.addWidget(self.random_button)
        self.main_layout.addWidget(self.limit_random_frame)

        self.sa = QScrollArea()
        self.sa.setWidgetResizable(True)
        self.sa.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.sa.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.sa.setStyleSheet(
            """
            background-color: #303030;
            border-radius: 5px;
            """
        )

        self.history_area = QFrame()
        self.history_layout = QVBoxLayout(self.history_area)

        self.history_area.setLayout(self.history_layout)
        self.history_layout.setContentsMargins(5, 5, 5, 5)
        self.history_layout.setSpacing(5)
        self.history_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter
        )

        self.sa.setWidget(self.history_area)

        self.main_layout.addWidget(self.sa)
        self.load_history()

    def load_history(self) -> None:
        history = file_management.get_history()
        for tag in history:
            l = HistoryWidget(tag)
            l.clicked.connect(self.copy_text)
            self.history_layout.addWidget(l)

    def copy_text(self, text: str, _, limit: int, random: bool) -> None:
        self.search_bar.setText(text)
        self.limit_spin.setValue(limit)
        # once again, so stupid (im stupid)
        self.random_button.setChecked(not random)
        self.random_button.update_text_color()
        self.random_button.set_stylesheet("#303030")

    def remove_tag(self, index: int):
        search_text = self.search_bar.text()
        parsed_search = parse(search_text, gelb_ready=True)
        parsed_search.pop(index)
        self.search_bar.setText(" ".join(parsed_search))

    class RandomButton(QPushButton):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, *kwargs)

            self.setFixedSize(75, 40)

            self.main_font = QFont("Jetbrains Mono", 12)
            self.main_font.setPointSize(12)
            self.setFont(self.main_font)

            self.text_color = "#b5e48c"

            self.set_stylesheet("#303030")
            self.clicked.connect(self.update_text_color)
            self.setCheckable(True)

        def set_stylesheet(self, color: str) -> None:

            self.setStyleSheet(
                f"""
                *{{
                    background-color: {color};
                    color: {self.text_color};
                    border-radius: 5px;
                }}
                #main-frame {{
                    border: 1px solid hsla(0, 0%, 90%, 10%)
                }}
                """
            )

        def update_text_color(self):
            if self.isChecked():
                self.text_color = "#c1121f"
                self.set_stylesheet("#404040")
            else:
                self.text_color = "#b5e48c"
                self.set_stylesheet("#404040")

        def mousePressEvent(self, event: QMouseEvent, /) -> None:
            self.main_font.setPointSize(10)
            self.setFont(self.main_font)
            self.clicked.emit()

            self.update_text_color()

            return super().mousePressEvent(event)

        def mouseReleaseEvent(self, event: QMouseEvent, /) -> None:
            self.update_text_color()
            self.main_font.setPointSize(12)
            self.setFont(self.main_font)

            return super().mouseReleaseEvent(event)

        def enterEvent(self, event: QEnterEvent, /) -> None:
            self.set_stylesheet("#404040")
            return super().enterEvent(event)

        def leaveEvent(self, event: QEvent, /) -> None:
            self.set_stylesheet("#303030")
            return super().leaveEvent(event)


class HistoryWidget(QFrame):

    clicked = Signal(str, object, int, bool)

    def __init__(self, tag, *args, **kwargs):
        super().__init__(*args, *kwargs)

        self.setObjectName("history-widget")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.set_stylesheet("#303030")
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self.main_layout = QHBoxLayout(self)
        self.setLayout(self.main_layout)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.main_layout.setAlignment(
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft
        )

        self.info_frame = QFrame()
        self.info_layout = QVBoxLayout(self.info_frame)
        self.info_frame.setLayout(self.info_layout)
        self.info_layout.setContentsMargins(5, 5, 5, 5)
        self.info_layout.setSpacing(0)
        self.info_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.limit_label = QLabel(f"{tag['limit']}", self)
        self.random_label = QLabel(f"Random", self)

        self.limit_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.random_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.random = tag["random"]
        if not tag["random"]:
            color = "#c1121f"
        else:
            color = "#b5e48c"

        self.random_label.setStyleSheet(f"color: {color};")
        self.limit_label.setFont(QFont("Jetbrains Mono", 14))

        self.info_layout.addWidget(self.limit_label)
        self.info_layout.addWidget(self.random_label)
        self.main_layout.addWidget(self.info_frame)

        self.text = self.format_text(tag["tags"])
        self.label = QLabel(self.text)
        self.label.setFont(QFont("Jetbrains Mono", 14))

        self.main_layout.addWidget(self.label)

    def format_text(self, tags: str) -> str:
        string = ""
        for tag in tags:
            text = tag.replace("+~+", " ~ ")
            string += f"{text} "
        return string

    def set_stylesheet(self, color: str):
        self.setStyleSheet(
            f"""
            #history-widget{{
                border: 1px solid white;
            }}
            *{{
                background-color: {color};
                color: white;
                border-radius: 5px;
            }}
            """
        )

    def mousePressEvent(self, ev: QMouseEvent, /) -> None:
        self.clicked.emit(self.text, self, int(self.limit_label.text()), self.random)
        return super().mousePressEvent(ev)

    def enterEvent(self, event: QEnterEvent, /) -> None:
        self.set_stylesheet("#404040")
        return super().enterEvent(event)

    def leaveEvent(self, event: QEvent, /) -> None:
        self.set_stylesheet("#303030")
        return super().leaveEvent(event)


class TagGraph(QScrollArea):

    widgetRemoved = Signal(int)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, *kwargs)

        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.setWidgetResizable(True)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.setStyleSheet(
            """
            background-color: #303030;
            color: white;
            border-radius: 5px;
            """
        )

        self.main_widget = QFrame()
        self.main_layout = QVBoxLayout(self.main_widget)
        self.main_widget.setLayout(self.main_layout)
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        self.main_layout.setSpacing(5)
        self.main_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter
        )

        self.setWidget(self.main_widget)

        self.tags = []
        self.raw_text = ""

    def update_tag_graph(self, text: str) -> None:
        self.raw_text = text
        tags = parse(text)

        while (child := self.main_layout.takeAt(0)) != None:
            if child.widget() and isinstance(child.widget(), QLabel):
                child.widget().deleteLater()
        self.tags = []

        for tag in tags:
            if tag:
                l = self.TagWidget(tag)
                l.clicked.connect(self.remove_tag)
                self.tags.append([tag, l])
                self.main_layout.addWidget(l)

    def remove_tag(self, text, widget):
        index = self.main_layout.indexOf(widget)
        self.widgetRemoved.emit(index)
        self.main_layout.removeWidget(widget)
        widget.deleteLater()

    class TagWidget(QLabel):

        clicked = Signal(str, object)

        def __init__(self, *args, **kwargs):
            super().__init__(*args, *kwargs)

            self.setFixedHeight(50)
            self.setFont(QFont("Jetbrains Mono", 16))
            self.setObjectName("tag-widget")
            self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            self.set_stylesheet("#303030")
            self.setCursor(Qt.CursorShape.PointingHandCursor)

        def set_stylesheet(self, color: str):
            self.setStyleSheet(
                f"""
                #tag-widget{{
                    border: 1px solid white;
                }}
                *{{
                    background-color: {color};
                    color: white;
                    border-radius: 5px;
                }}
                """
            )

        def mousePressEvent(self, ev: QMouseEvent, /) -> None:
            self.clicked.emit(self.text(), self)
            return super().mousePressEvent(ev)

        def enterEvent(self, event: QEnterEvent, /) -> None:
            self.set_stylesheet("#404040")
            return super().enterEvent(event)

        def leaveEvent(self, event: QEvent, /) -> None:
            self.set_stylesheet("#303030")
            return super().leaveEvent(event)


class IconButton(QFrame):

    clicked = Signal()

    def __init__(self, text: str, icon: QIcon, *args, **kwargs):
        super().__init__(*args, *kwargs)

        self.setFixedSize(250, 50)
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
        self.label.setFont(self.main_font)
        if self.rect().contains(event.pos()):
            self.clicked.emit()

        self.icon_button.setIconSize(QSize(40, 40))
        return super().mouseReleaseEvent(event)

    def enterEvent(self, event: QEnterEvent, /) -> None:
        self.set_stylesheet("#404040")
        return super().enterEvent(event)

    def leaveEvent(self, event: QEvent, /) -> None:
        self.set_stylesheet("#303030")
        return super().leaveEvent(event)

    def doubleClickEvent(self, event: QMouseEvent, /) -> None:
        event.ignore()
