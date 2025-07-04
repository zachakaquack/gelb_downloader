import os
from os.path import exists
from ssl import AlertDescription
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


class ImageFrame(QFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, *kwargs)

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setStyleSheet(
            """
            QFrame{
                background-color: #1e1e1e;
                color: white;
            }
            """
        )

        self.movie_extensions = [
            ".mp4",
            ".gif",
        ]

        self.main_layout = QVBoxLayout(self)
        self.setLayout(self.main_layout)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(0)
        self.main_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter
        )

        self.image_label = QLabel("", self)
        self.main_layout.addWidget(self.image_label)

        self.progress = None

    def progress_bar(self, count, total) -> None:
        # text, so it means we can load the progress bar
        if self.image_label.text():
            self.image_label.hide()

        if not self.progress:
            self.progress = QProgressBar(self)
            self.main_layout.insertWidget(0, self.progress)
            self.progress.setMinimum(0)
            self.progress.setMaximum(total)

        self.progress.setValue(count)
        self.progress.setMaximum(total)

    def remove_progress(self) -> None:
        self.image_label.show()
        if self.progress:
            self.progress.hide()
            self.progress.deleteLater()
            self.progress = None

    def load_no_image(self):
        self.remove_progress()

        self.image_label.setPixmap(QPixmap())
        self.image_label.setText("No Images Left!")
        self.image_label.setFont(QFont("Jetbrains Mono", 20))

    def load_new_image(self, image_path: str) -> None:
        self.remove_progress()
        _, extension = os.path.splitext(image_path)
        if extension in self.movie_extensions:
            movie = self.get_resized_movie(QMovie(f"{image_path}"))
            self.image_label.setMovie(movie)
            movie.start()
        else:
            pixmap = QPixmap(image_path)
            scaled_pixmap = pixmap.scaled(
                QSize(100000, 1080),
                aspectMode=Qt.AspectRatioMode.KeepAspectRatio,
                mode=Qt.TransformationMode.SmoothTransformation,
            )
            self.image_label.setPixmap(scaled_pixmap)

    def get_resized_movie(self, movie: QMovie) -> QMovie:
        movie.jumpToFrame(0)

        size = movie.currentPixmap().size()
        if size.isEmpty():
            return movie

        goal_height = 1080
        goal_size = QSize(9999, goal_height)

        scaled_size = size.scaled(goal_size, Qt.AspectRatioMode.KeepAspectRatio)
        movie.setScaledSize(scaled_size)
        return movie
