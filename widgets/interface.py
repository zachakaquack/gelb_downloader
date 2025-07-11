import os
from AsyncioPySide6 import AsyncioPySide6
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from other import file_management

# thanks python
try:
    from image_area import ImageFrame
except ModuleNotFoundError:
    from widgets.image_area import ImageFrame

try:
    from side_bar import SideBar
except ModuleNotFoundError:
    from widgets.side_bar import SideBar

try:
    from tag_popup import TagPopup
except ModuleNotFoundError:
    from widgets.tag_popup import TagPopup


try:
    from .other import serverside
except ModuleNotFoundError:
    from other import serverside

try:
    from post_popup import TagBar
except ModuleNotFoundError:
    from widgets.post_popup import TagBar

try:
    from overlay import Overlay
except ModuleNotFoundError:
    from widgets.overlay import Overlay


class Interface(QFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, *kwargs)

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setStyleSheet(
            """
            background-color: #1e1e1e;
            """
        )

        self.main_layout = QHBoxLayout(self)
        self.setLayout(self.main_layout)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.main_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter
        )

        self.tag_bar = TagBar()
        self.image_area = ImageFrame()
        self.side_bar = SideBar()

        self.side_bar.clicked.connect(self.process_sidebar)

        self.main_layout.addWidget(self.tag_bar)
        self.main_layout.addWidget(self.image_area)
        self.main_layout.addWidget(self.side_bar)

        self.main_layout.setStretch(0, 15)
        self.main_layout.setStretch(1, 75)
        self.main_layout.setStretch(2, 10)

        self.current_image_path = ""
        self.tag_popup = None

        self.first_time_check()

    # def keyPressEvent(self, event: QKeyEvent, /) -> None:
    #     if event.key() == Qt.Key.Key_Space:
    #         self.first_time_check()
    #
    #     return super().keyPressEvent(event)

    def first_time_check(self) -> None:
        config = file_management.get_config()
        if config["settings"]["config_set"] == True:
            self.load_new_image()
            return

        # config is not set. launch the starter popup
        self.overlay = Overlay()
        # delay to make it appear over the mainwindow
        QTimer.singleShot(150, self.overlay.show)

    def process_sidebar(self, text: str) -> None:
        match text:
            case "save":
                self.save_image()
            case "delete":
                self.delete_image()
            case "search":
                self.launch_popup()
            case "refresh":
                self.load_new_image()
            case _:
                print(text)

    def save_image(self) -> None:
        saved_path = file_management.get_saved_path()
        file_name = os.path.basename(self.current_image_path)
        os.rename(self.current_image_path, f"{saved_path}/{file_name}")
        self.load_new_image()

    def delete_image(self) -> None:
        deleted_path = file_management.get_deleted_path()
        file_name = os.path.basename(self.current_image_path)
        os.rename(self.current_image_path, f"{deleted_path}/{file_name}")
        self.load_new_image()

    def load_new_image(self) -> None:
        download_path = file_management.get_download_path().glob("**/*")
        files = [x for x in download_path if x.is_file()]

        if files:
            self.current_image_path = files[0]
            self.image_area.load_new_image(f"{files[0]}")
            self.tag_bar.refresh(f"{files[0]}")
        else:
            self.image_area.load_no_image()
            self.tag_bar.remove_all()

    def launch_popup(self):
        self.popup = TagPopup()
        self.popup.search.connect(self.download_images)
        self.popup.show()

    def done_downloading(self) -> None:
        if self.popup:
            self.popup.close()

        self.side_bar.setEnabled(True)

        self.load_new_image()

    def download_images(self):
        self.side_bar.setEnabled(False)
        self.worker = serverside.ImageWorker()

        self.image_area.progress_bar(0, 0)
        self.worker.progress.connect(self.image_area.progress_bar)
        self.worker.done.connect(self.done_downloading)

        AsyncioPySide6.runTask(self.worker.download_search())
