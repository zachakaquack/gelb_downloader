from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
import os
import requests
from other import file_management
from AsyncioPySide6 import AsyncioPySide6
import webbrowser


class TagBar(QScrollArea):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, *kwargs)

        self.setFixedWidth(288)
        self.main_widget = QFrame()
        self.setWidget(self.main_widget)
        self.setWidgetResizable(True)
        # self.setStyleSheet("background-color: #303030;")

        self.main_layout = QVBoxLayout(self.main_widget)
        self.main_widget.setLayout(self.main_layout)
        self.main_layout.setContentsMargins(5, 5, 5, 0)
        self.main_layout.setSpacing(5)
        self.main_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft
        )

    def loading(self):
        self.loading_label = QLabel("Loading...")
        self.loading_label.setStyleSheet("color: white;")
        self.loading_label.setFont(QFont("Jetbrains Mono", 20, 500))
        self.loading_label.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.main_layout.addWidget(self.loading_label)

    def refresh(self, filepath) -> None:

        self.remove_all()
        self.loading()

        self.filepath = filepath
        self.filename = os.path.basename(self.filepath)
        self.filename = self.filename.split("_")[1]
        self.post_id = os.path.splitext(self.filename)[0]
        self.get_tags(self.post_id)

    def remove_all(self) -> None:
        while (child := self.main_layout.takeAt(0)) != None:
            if child.widget():
                child.widget().deleteLater()

    def load_tags(self, tag_lists) -> None:
        """
        this following code sucks. i know it sucks. but:
        the way the tags are returned are in this order:
        0: tag
        1: artist
        2: unused
        3: copyright
        4: character
        5: metadata
        6: depracated

        but the way they are actually displayed are different
        they are displayed like this:
        artist
        character
        copyright
        metadata
        tag

        and somewhere in there is the dep'd tags... no idea where
        """

        self.remove_all()

        artists = tag_lists[1]
        characters = tag_lists[4]
        copyrights = tag_lists[3]
        metadatas = tag_lists[5]
        tags = tag_lists[0]
        deps = tag_lists[6]

        title_font = QFont("Jetbrains Mono", 12, weight=500)
        for tag_group in [artists, characters, copyrights, metadatas, deps, tags]:
            """
            tag_group = list[3]
            0: "title"
            1: color
            2: tags
            """

            # do not add if no tags
            if not tag_group[2]:
                continue

            # widget that contains the group, and its tags
            widget = QFrame()
            layout = QVBoxLayout(widget)
            widget.setLayout(layout)

            # the spacing between the title and the tags
            layout.setSpacing(0)
            layout.setContentsMargins(0, 0, 0, 0)

            title_label = QLabel(f"{tag_group[0]}")
            title_label.setFont(title_font)
            title_label.setStyleSheet("color: white;")
            layout.addWidget(title_label)

            for tag in tag_group[2]:
                tag = Tag(tag, tag_group[1])
                layout.addWidget(tag)

            self.main_layout.addWidget(widget)

    def get_tags(self, post_id: int) -> None:
        self.worker = TagGetterWorker()
        self.worker.done.connect(self.load_tags)

        AsyncioPySide6.runTask(self.worker.get_tags(post_id))
        # self.worker.get_tags_test(post_id)


class Tag(QFrame):
    def __init__(self, tag, color, *args, **kwargs):
        super().__init__(*args, *kwargs)

        self.help_url = "https://gelbooru.com/index.php?page=wiki&s=list&search="
        self.tag_url = "https://gelbooru.com/index.php?page=post&s=list&tags="

        self.tag = tag
        self.color = color

        self.main_layout = QHBoxLayout(self)
        self.setLayout(self.main_layout)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(2)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.help_label = QLabel("?")
        self.help_label.setStyleSheet(f"color: #6dc9f4")
        self.help_label.setCursor(Qt.CursorShape.PointingHandCursor)
        self.help_label.mousePressEvent = self.open_wiki

        self.tag_label = QLabel(f"{self.tag['name']}")
        self.tag_label.setStyleSheet(f"color: {self.color};")
        self.tag_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.tag_label.setCursor(Qt.CursorShape.PointingHandCursor)
        self.tag_label.mousePressEvent = self.open_tag

        self.count_label = QLabel(f"{tag["count"]}")
        self.count_label.setStyleSheet(f"color: gray;")

        self.main_layout.addWidget(self.help_label)
        self.main_layout.addWidget(self.tag_label)
        self.main_layout.addWidget(self.count_label)

    def open_tag(self, _) -> None:
        webbrowser.open(f"{self.tag_url}{self.tag['name']}")

    def open_wiki(self, _) -> None:
        webbrowser.open(f"{self.help_url}{self.tag['name']}")


class TagGetterWorker(QObject):

    done = Signal(list)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, *kwargs)

    async def get_tags(self, post_id):
        config = file_management.get_config()
        user_settings = config["user_info"]

        api_key = user_settings["api_key"]
        user_id = user_settings["user_id"]

        base = (
            "https://gelbooru.com/index.php?page=dapi&q=index&json=1"
            + f"&api_key={api_key}&user_id={user_id}"
        )

        # getting the tags of a post
        url = f"{base}&tags=id:{post_id}&s=post"

        r = requests.get(f"{base}/{url}")
        tags = r.json()["post"][0]["tags"]

        # getting which type of tag each tag is
        r = requests.get(f"{base}/&s=tag&names={tags}")

        # sort for each of the 6 categories of tags
        tag_lists = [
            ["Tag", "#6dc9f4", []],  # normal tag
            ["Artist", "#dd4610", []],  # artist
            [],  # unused by devs
            ["Copyright", "#c814be", []],  # copyright
            ["Character", "green", []],  # character
            ["Metadata", "orange", []],  # metadata
            ["Depracated", "gray", []],  # depracated tags
            # artist: #dd4610
        ]

        tags = r.json()["tag"]

        for tag in tags:
            tag_type = tag["type"]
            tag_lists[tag_type][2].append(tag)

        self.done.emit(tag_lists)
