from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

import json
from other import file_management

try:
    from other.buttons import Button
except ModuleNotFoundError:
    from ..other.buttons import Button


class Overlay(QScrollArea):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, *kwargs)

        # self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowStaysOnTopHint)
        # self.show()

        self.setStyleSheet(
            """
            background-color: #1e1e1e;
            color: white;
            """
        )

        self.setFixedSize(500, 500)

        self.main_widget = QFrame()
        self.setWidget(self.main_widget)
        self.setWidgetResizable(True)

        self.main_layout = QVBoxLayout(self.main_widget)
        self.main_widget.setLayout(self.main_layout)
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        self.main_layout.setSpacing(5)
        self.main_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter
        )

        self.title_font = QFont("Jetbrains Mono", 20, weight=500)
        self.label_font = QFont("Jetbrains Mono", 15)

        self.title_label = QLabel("Welcome!")
        self.title_label.setFont(self.title_font)
        self.main_layout.addWidget(self.title_label)

        self.description_label = QTextEdit(
            """
            gelb_downloader is a program used to search for and sort through
            different images from Gelbooru. There are some things that you need to fill
            out to be able to use this program;"""
        )
        self.description_label.setSizePolicy(
            QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum
        )
        self.description_label.setReadOnly(True)
        self.description_label.setFont(self.label_font)
        self.main_layout.addWidget(self.description_label)

        # default download path
        d = QLabel("Default Download Path")
        d.setFont(self.label_font)

        self.down_fold_picker = self.FolderPicker("download")

        self.download = self.Pair()
        self.download.add_pair(d, self.down_fold_picker)
        self.main_layout.addWidget(self.download)

        # saved
        d = QLabel("Default Saved Path")
        d.setFont(self.label_font)
        self.save_fold_picker = self.FolderPicker("saved")

        self.saved = self.Pair()
        self.saved.add_pair(d, self.save_fold_picker)
        self.main_layout.addWidget(self.saved)

        # deleted
        d = QLabel("Default Deleted Path")
        d.setFont(self.label_font)
        self.deleted_fold_picker = self.FolderPicker("deleted")

        self.deleted = self.Pair()
        self.deleted.add_pair(d, self.deleted_fold_picker)
        self.main_layout.addWidget(self.deleted)

        # api key
        d = QLabel("API Key")
        d.setFont(self.label_font)

        self.api_input = self.Input("api")
        self.api_key = self.Pair()
        self.api_key.add_pair(d, self.api_input)
        self.main_layout.addWidget(self.api_key)

        # user id
        d = QLabel("User ID")
        d.setFont(self.label_font)

        self.user = self.Input("id")
        self.user_id = self.Pair()
        self.user_id.add_pair(d, self.user)
        self.main_layout.addWidget(self.user_id)

        # done

        self.label = QTextEdit(
            "You can access these again in settings. This window will not pop up again when you close!"
        )
        self.label.setFont(self.label_font)
        self.label.setReadOnly(True)
        self.main_layout.addWidget(self.label)

        self.close_button = Button("Close")
        self.main_layout.addWidget(self.close_button)
        self.close_button.clicked.connect(self.handle_close)

    def handle_close(self) -> None:

        config = file_management.get_config()
        config["settings"]["config_set"] = True

        config_path = file_management.get_config_path()
        with open(f"{config_path}", "w") as f:
            f.write(json.dumps(config, indent=4))

        self.close()

    def keyPressEvent(self, event: QKeyEvent, /) -> None:
        if event.key() == Qt.Key.Key_Escape:
            self.close()

    class Input(QFrame):
        def __init__(self, type, *args, **kwargs):
            super().__init__(*args, *kwargs)

            self.type = type

            self.setSizePolicy(
                QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
            )

            self.main_layout = QHBoxLayout(self)
            self.setLayout(self.main_layout)
            self.main_layout.setContentsMargins(5, 5, 5, 5)
            self.main_layout.setSpacing(5)
            self.main_layout.setAlignment(
                Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter
            )

            self.input = QLineEdit()
            self.input.setStyleSheet("background-color: #404040;")
            self.input.setSizePolicy(
                QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
            )
            self.input.setFont(QFont("Jetbrains Mono", 16))

            self.confirm = Button("Save")
            self.confirm.setFixedHeight(50)
            self.confirm.clicked.connect(self.handle_save)

            self.main_layout.addWidget(self.input)
            self.main_layout.addWidget(self.confirm)

        def handle_save(self):
            text = self.input.text()
            match self.type:
                case "api":
                    file_management.save_api_key(text)
                case "id":
                    file_management.save_user_id(text)
                case _:
                    print(self.type, text)

    class FolderPicker(Button):
        def __init__(self, type, *args, **kwargs):
            super().__init__("Pick a folder...", *args, *kwargs)

            self.type = type

            self.set_font_sizes(10, 12)

            self.setSizePolicy(
                QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed
            )

            self.setMinimumWidth(150)
            self.setFixedHeight(50)

            self.dialog = QFileDialog()
            self.dialog.setFileMode(QFileDialog.FileMode.Directory)
            self.dialog.setOption(QFileDialog.Option.ShowDirsOnly, True)
            self.dialog.setWindowTitle("Open Downloads")
            self.dialog.setDirectory("~/.config/gelbooru-downloader")

        def mouseReleaseEvent(self, event: QMouseEvent, /) -> None:

            if self.dialog.exec() == QDialog.DialogCode.Accepted:
                dirs: list = self.dialog.selectedFiles()
                dir = dirs[0]
                if dir:
                    self.label_text = f"{dir[0]}"
                    self.label.setText(f"{dir[0]}")
                    self.set_font_sizes(10, 10)

                    # save
                    match self.type:
                        case "download":
                            file_management.save_downloads_folder(dir)
                        case "saved":
                            file_management.save_saved_folder(dir)
                        case "deleted":
                            file_management.save_deleted_folder(dir)

            return super().mouseReleaseEvent(event)

    class Pair(QFrame):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, *kwargs)

            self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

            self.setStyleSheet(
                "border-radius: 5px; background-color: #303030; color: white;"
            )

            self.main_layout = QVBoxLayout(self)
            self.setLayout(self.main_layout)
            self.main_layout.setContentsMargins(5, 5, 5, 5)
            self.main_layout.setSpacing(5)
            self.main_layout.setAlignment(
                Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft
            )

        def add_pair(self, text: QLabel, input: QWidget) -> None:
            self.main_layout.addWidget(text)
            self.main_layout.addWidget(input)
