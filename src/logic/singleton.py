from typing import *
import os
from pathlib import Path
from src.pages import logWindow
from src.utils.paths import get_data_path
from src.logic.graphWindowData import GraphWindow
import peewee as pw
from src.database.database_setup import initialize_db, close_db


# TODO later we can have the user adjust the move amount
class Singleton:
    """Is a singleton to hold all temporary data that the program needs

    Attributes:
        videos (list[str]): List of path strings for videos uploaded
        _selectedVideos (dict[str, dict[str, bool | List[int, int]]]):
            dict[path, dict[state: bool, coor: list[int, int]]]
    """

    _instance = None
    _tempFolder: str
    _tempFolderPictures: str
    _selectedVideos: dict  #: dict[str, dict[str, bool | List[int, int]]]
    _moveAmount: int
    _databaseVideoFolder: str
    _graphWindowObj: GraphWindow
    _database: pw.SqliteDatabase
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            # Create the instance if it doesn't exist
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, value=None):
        # 1. Check if the instance already has the '_initialized' flag
        if not hasattr(self, "_initialized"):
            # print("Running __init__ for the first time...")
            self._tempFolder = get_data_path("videos")
            self._tempFolderPictures = get_data_path("pictures")
            self._databaseVideoFolder = get_data_path("databaseVideos")
            os.makedirs(self._tempFolder, exist_ok=True)
            os.makedirs(self._tempFolderPictures, exist_ok=True)
            os.makedirs(self._databaseVideoFolder, exist_ok=True)
            self._selectedVideos = {}
            self._moveAmount = 50
            self._graphWindowObj = GraphWindow()

            # Put all your heavy setup, database connections, etc. here
            self.value = value

            # 2. Set the flag so this block is skipped next time
            self._initialized = True
        else:
            pass
            # print("__init__ was called again, but setup was bypassed.")

    # def init_graphWindowObj(self) -> None:
    #     self._graphWindowObj = GraphWindow()

    # def init_databaseObj(self) -> None:
    #     self._databse = initialize_db()

    # def get_databaseObj(self) -> pw.SqliteDatabase:
    #     return self._database

    def get_graphWindowObj(self) -> GraphWindow:
        return self._graphWindowObj

    def get_tempFolder(self):
        return self._tempFolder

    def get_tempFolderPictures(self):
        return self._tempFolderPictures

    def get_databaseVideoFolder(self):
        return self._databaseVideoFolder

    def get_selectedVideos(self):
        self.get_all_temp_files()
        return self._selectedVideos

    def set_selectedVideo(self, video: str, state: bool) -> None:
        self.get_all_temp_files()
        self._selectedVideos[video]["state"] = state

    def update_selectedVideoCoordinates(self, video: str, direction: str) -> None:
        """
        direction must be "up", "down", "left", "right" only!!!!
        amount must be greather than 0
        """
        print(self._selectedVideos[video])
        amount = self._moveAmount
        if amount < 0:
            print(
                "THE AMOUNT SENT TO update_selectedVideoCoordinates in the singleton class MUST be greather than 0!!!"
            )
            logWindow.addLog(1, f"The amount MUST be greather than 0!")
            return
        match direction:
            case "up":
                if self._selectedVideos[video]["coor"][1] - amount >= 0:
                    self._selectedVideos[video]["coor"][1] -= amount
                else:
                    logWindow.addLog(1, f"Cannot move {video} any higher")
            case "down":
                self._selectedVideos[video]["coor"][1] += amount
            case "left":
                if self._selectedVideos[video]["coor"][0] - amount >= 0:
                    self._selectedVideos[video]["coor"][0] -= amount
                else:
                    logWindow.addLog(1, f"Cannot move {video} any more to the left!")
            case "right":
                self._selectedVideos[video]["coor"][0] += amount
        print(self._selectedVideos[video])
        print("\n\n\n")

    def delete_video(self, video: str) -> None:
        if video in self._selectedVideos:
            del self._selectedVideos[video]
        if os.path.exists(video):
            os.remove(video)
            logWindow.addLog(0, f"{video} has been deleted.")
            print(f"{video} has been deleted.")
        else:
            logWindow.addLog(
                2,
                f"{video} has been requested to be deleted but the file cannot be found",
            )

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Singleton, cls).__new__(cls)
        return cls._instance

    def get_all_temp_files(self, recursive=False) -> List[str]:
        """
        Returns a list of all files in a folder as absolute paths.

        :param recursive: If True, searches all subfolders. If False, only the top folder.
        :return: A list of file path strings.
        """
        path = self._tempFolder
        if not os.path.isdir(path):
            return []

        files: List[str] = []
        try:
            if recursive:
                for root, _, filenames in os.walk(path):
                    for name in filenames:
                        files.append(os.path.join(root, name))
            else:
                with os.scandir(path) as it:
                    for entry in it:
                        if entry.is_file():
                            files.append(entry.path)
        except OSError:
            return []

        for file in files:
            if file not in self._selectedVideos:
                self._selectedVideos[file] = {"state": False, "coor": [0, 0]}

        return files
