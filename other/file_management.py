from pathlib import Path
import json


def get_config_folder() -> Path:
    # make notewriter if it doesn't exist
    home = Path.home()
    gelbooru_path = Path(f"{home}/.config/gelbooru-downloader")
    gelbooru_path.mkdir(parents=True, exist_ok=True)

    # both are created now; continue
    return gelbooru_path


def get_config() -> dict:
    path = get_config_folder()
    config = Path(f"{path}/config.json")

    download_path = Path(f"{path}/downloaded")
    download_path.mkdir(parents=True, exist_ok=True)

    deleted_path = Path(f"{path}/deleted")
    deleted_path.mkdir(parents=True, exist_ok=True)

    saved_path = Path(f"{path}/saved")
    saved_path.mkdir(parents=True, exist_ok=True)

    # check if the config file exists
    if not config.is_file():

        # general data
        data = {
            "downloads": {
                "downloads": f"{download_path}",
                "deleted": f"{deleted_path}",
                "saved": f"{saved_path}",
            },
            "user_info": {
                "api_key": "YOUR_API_KEY_HERE",
                "user_id": "YOUR_USER_ID_HERE",
            },
            "search": {
                "tags": ["kasane_teto", "rating:general"],
                "limit": 5,
                "random": True,
            },
            "search_history": [
                {
                    "tags": ["kasane_teto", "rating:general"],
                    "limit": 5,
                    "random": True,
                },
            ],
        }

        # create the file and insert basic data
        with open(config, "w") as f:
            f.write(json.dumps(data, indent=4))
            return data
    else:
        # file exists, just return it
        with open(config, "r") as f:
            data = json.loads(f.read())
            return data


def get_download_path() -> Path:
    path = get_config_folder()
    download_path = Path(f"{path}/downloaded")
    download_path.mkdir(exist_ok=True)
    return download_path


def get_deleted_path() -> Path:
    path = get_config_folder()
    deleted_path = Path(f"{path}/deleted")
    deleted_path.mkdir(exist_ok=True)
    return deleted_path


def get_saved_path() -> Path:
    path = get_config_folder()
    saved_path = Path(f"{path}/saved")
    saved_path.mkdir(exist_ok=True)
    return saved_path


def get_history() -> dict:
    data = get_config()
    return data["search_history"]


def get_config_path() -> Path:
    path = get_config_folder()
    config = Path(f"{path}/config.json")
    return config


def save_search(tags: list, limit: int, random: bool) -> None:
    config_path = get_config_path()
    data = get_config()

    # edit current search
    search = data["search"]

    # add the search history if not most recent
    if (
        tags == search["tags"]
        and limit == search["limit"]
        and random == search["random"]
    ):
        return

    search["tags"] = tags
    search["limit"] = limit
    search["random"] = random

    data["search_history"].insert(0, search)

    # write
    with open(f"{config_path}", "w") as f:
        f.write(json.dumps(data, indent=4))
