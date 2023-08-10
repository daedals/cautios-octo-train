"""proof of concept for a module that changes json data from within a window"""

import sys
import json
from COTdataclasses import SessionData
from datetime import datetime


class SessionHandler:
    """ wrapper for dict able to read from json"""

    def __init__(self):
        self.json_data = {}
        self.session_data: SessionData = None
        self._path = "session_data.json"

    def initialize(self, video_file_path: str, gps_file_path: str, image_width: int, image_height: int, creation_date: datetime = datetime.now()):
        self.session_data = SessionData(video_file_path, gps_file_path, image_width, image_height, creation_date)

    def load(self, _path= None):
        """load data from json in static location"""
        if _path is None:
            _path = self._path
        else:
            self._path = _path
        try:
            with open(_path, "r", encoding="ascii") as file:
                self.json_data = json.load(file)
            return True
        except FileNotFoundError:
            # If the file doesn't exist
            print("file not found")
            return False

    def save(self, _path= None):
        """save data to json in static location of create if not available"""
        if any(value is None for _, value in self.json_data.items()):
            return
        if _path is None:
            _path = self._path
        with open(_path, "w", encoding="ascii") as file:
            json.dump(self.json_data, file, indent=4)

    def add(self, key: str, value):
        """ wrapper for dict accessor """
        self.json_data[key] = value

    def get(self, *args, **kwargs):
        """ wrapper for dict getter """
        return self.json_data.get(*args, **kwargs)
