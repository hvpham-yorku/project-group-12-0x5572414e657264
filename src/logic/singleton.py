from typing import *
import os
from pathlib import Path
from src.pages import logWindow


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
    _selectedVideos: dict[str, dict[str, bool | List[int, int]]]
    _moveAmount: int

    def __init__(self):
        self._tempFolder = os.path.join(os.getcwd(), "assets/videos")
        self._tempFolderPictures = os.path.join(os.getcwd(), "assets/pictures")
        self._selectedVideos = {}
        self._moveAmount = 50

    def get_tempFolder(self):
        return self._tempFolder

    def get_tempFolderPictures(self):
        return self._tempFolderPictures

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
        :return: A list of Path objects (which can be easily converted to strings).
        """
        # Convert string input to a Path object
        path = Path(self._tempFolder)

        # Check if the path exists and is a directory
        if not path.is_dir():
            return f"Error: {self._tempFolder} is not a valid directory."

        # Use rglob('*') for recursive or glob('*') for top-level only
        search_pattern = "**/*" if recursive else "*"

        # Filter for files only (ignoring folders in the results)
        files = [f.absolute() for f in path.glob(search_pattern) if f.is_file()]

        files = [str(x) for x in files]

        for file in files:
            if file not in self._selectedVideos:
                self._selectedVideos[file] = {"state": False, "coor": [0, 0]}

        return files
