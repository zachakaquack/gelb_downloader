import json
from other import file_management
from python_gelbooru import AsyncGelbooru
from pathlib import Path
from PySide6.QtCore import QObject, Signal


class ImageWorker(QObject):
    progress = Signal(int, int)
    done = Signal()
    error = Signal(str)

    def __init__(self):
        super().__init__()

    async def download_search(self):
        try:
            config = file_management.get_config()
            user_settings = config["user_info"]
            search_settings = config["search"]

            api_key = user_settings["api_key"]
            user_id = user_settings["user_id"]

            tags = search_settings["tags"]
            limit = search_settings["limit"]
            random = search_settings["random"]
            download_path = config["downloads"]["downloads"]

            async with AsyncGelbooru(api_key=api_key, user_id=user_id) as gel:
                posts = await gel.search_posts(tags, limit=limit, random=random)

                total = len(posts)
                self.progress.emit(0, total)
                for i, post in enumerate(posts):
                    post_path = Path(f"{download_path}/{i+1}_{post.id}")
                    await post.async_download(str(post_path))
                    self.progress.emit(i + 1, total)

            self.done.emit()

        except Exception as e:
            self.error.emit(str(e))


async def get_tags_of_post(id: int) -> list:
    config = file_management.get_config()
    user_settings = config["user_info"]

    api_key = user_settings["api_key"]
    user_id = user_settings["user_id"]

    async with AsyncGelbooru(api_key=api_key, user_id=user_id) as gel:
        posts = await gel.search_posts(f"id:{id}", limit=1, random=False)
        return posts[0].tags
