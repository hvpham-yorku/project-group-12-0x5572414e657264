from typing import *
import os


class Singleton:
    """Is a singleton to hold all temporary data that the program needs

    Attributes:
        videos (list[str]): List of path strings for videos uploaded
    """

    _instance = None
    _videos: List[str]
    _tempFolder: str

    def __init__(self):
        self._videos = []
        self._tempFolder = os.path.join(os.getcwd(), "assets/databaseAssets")

    def get_videoList(self):
        return self._videos

    def get_tempFolder(self):
        return self._tempFolder

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Singleton, cls).__new__(cls)
        return cls._instance
