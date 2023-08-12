""" All handler class definitions 

GPSDataHandler
KeyFrameHandler
SessionHandler

"""

import json
import csv
from math import atan2
from datetime import time, datetime

from PySide6.QtWidgets import QMenuBar, QMenu
from PySide6.QtCore import Signal, QObject
from PySide6.QtGui import QAction

from COTdataclasses import GPSDatum, SessionData, KeyFrame, IntrinsicCameraParameters, ExtrinsicCameraParameters
from tools.math import determine_camera_parameters, distance_between_geo_coordinates


class GPSDataHandler(QObject):
    """Data container for GPS data from specific csv format"""

    gpsdatum_requested = Signal(GPSDatum)

    def __init__(self) -> None:
        super().__init__()
        self.data = []
        self._file_path :str = None

    def __getitem__(self, index: int) -> GPSDatum:
        return self.data[index]

    def read_csv_data(self, _file_path):
        """ Reads data from specific gps csv files and converts them to a list of tuples """

        # Return if function is called with the same argument
        if self._file_path is not None and _file_path.lower() == self._file_path.lower():
            return

        with open(_file_path, 'r', encoding='ascii') as file:

            # Discard data if a new file_path is provided
            if self.data is not None:
                del self.data
                self.data = []

            # Set file path
            self._file_path = _file_path

            # Read with csv module
            csv_reader = csv.reader(file)
            _ = next(csv_reader)  # skip the header line

            first_timestamp: int = None

            for row in csv_reader:
                try:
                    # catch all header values as strings
                    tid, lat, lon, speed, course, alt = row

                    # time id is given as a clock time in milliseconds, so 12:34 is 12340000
                    # gps coordinates seem to have been created only every second
                    # so it is converted to total amount of seconds
                    s = int(int(tid)/100)%100
                    m = int(int(tid)/10000)%100
                    h = int(int(tid)/1000000)

                    timestamp = 3600 * h + 60 * m + s

                    # remember first t
                    if first_timestamp is None:
                        first_timestamp = timestamp

                    row_data = GPSDatum(
                        time(hour=h, minute=m, second=s),
                        timestamp - first_timestamp,
                        # latitude and longitude are given in decimal geographical degrees multiplied by 100000
                        float(int(lat)) / 10**5,
                        float(int(lon)) / 10**5,
                        # speed is given in 10m/h, converted to km/h
                        float(int(speed)) / 10**2,
                        # course is not used
                        int(course),
                        # altitude is given in cm, converted to m
                        float(int(alt)) / 10**2
                        # gradient is added later
                    )

                    self.data.append(row_data)

                except Exception as exception:
                    print(
                        f'{exception}: Row {csv_reader.line_num} with values {row} could not be converted.'
                    )
            
            self.add_gradient()

    def add_gradient(self):
        """ adds the gradient value to all gpsdata """
        item_count = len(self.data)
        if item_count == 0:
            return
        
        gpsdatum: GPSDatum
        for i, gpsdatum in enumerate(self.data):
            # skip first and last item
            if i == 0 or i == item_count - 1:
                gpsdatum.gradient = 0
                continue

            gradient = 0
            gradients = []

            # get the preavious and following gpsdata
            previous: GPSDatum = self.data[i-1]
            following: GPSDatum = self.data[i+1]

            # calculate gradient from previous to current
            distance = distance_between_geo_coordinates(
                previous.latitude, previous.longitude,
                gpsdatum.latitude, gpsdatum.longitude
            )

            d_altitude = gpsdatum.altitude - previous.altitude

            if distance > 0:
                gradients.append(atan2(d_altitude, distance))

            # calculate gradient from current to following
            distance = distance_between_geo_coordinates(
                gpsdatum.latitude, gpsdatum.longitude,
                following.latitude, following.longitude
            )

            d_altitude = following.altitude - gpsdatum.altitude

            if distance > 0:
                gradients.append(atan2(d_altitude, distance))

            # take mean of calculated gradients
            if len(gradients) > 0:
                gradient = sum(gradients)/len(gradients)
            
            gpsdatum.gradient = gradient

    def request_gpsdatum(self, gpsdatum: GPSDatum):
        self.gpsdatum_requested.emit(gpsdatum)

    def list_data(self):
        """ generator for list of coordinates """
        gpsdatum: GPSDatum
        for gpsdatum in self.data:
            yield gpsdatum

    def list_of_coords_filtered(self):
        """ generator for list of coordinates with unique geographical coordinates"""
        gpsdatum: GPSDatum
        previous_lat: float = 0
        previous_lon: float = 0

        for gpsdatum in self.data:
            if previous_lat == gpsdatum.latitude and previous_lon == gpsdatum.longitude:
                continue

            previous_lat = gpsdatum.latitude
            previous_lon = gpsdatum.longitude

            yield gpsdatum

    def list_of_timestamps(self) -> list:
        """ provides list of timestamps"""
        return [gpsdatum.timestamp for gpsdatum in self.data]

    def closest_datum_by_timestamp(self, timestamp: int) -> GPSDatum:
        
        # find timestamp that is closest to the sought one
        timestamps = [*self.list_of_timestamps()]
        closest_timestamp = min(
            timestamps,
            key=lambda x:abs(x-timestamp)
        )
        return self.data[timestamps.index(timestamp)]
        


    @property
    def file_path(self):
        """ getter for file path """
        return self._file_path


class KeyFrameHandler(QObject):
    """ handles keyframes """

    keyframe_requested = Signal(KeyFrame)

    def __init__(self, menubar: QMenuBar) -> None:
        super().__init__()
        self.current_keyframe: KeyFrame = None
        self.data = []
        self.menu: QMenu = menubar.addMenu("Jump to Key Frame")

    def from_gpsdatum(self, gpsdatum: GPSDatum) -> KeyFrame:
        try:
            index = [keyframe.gps for keyframe in self.data].index(gpsdatum)
            return self.data[index]
        except ValueError:
            return None

    def request_keyframe(self, keyframe: KeyFrame) -> None:
        # add keyframe if its not already in there
        if keyframe not in self.data:
            self.data.append(keyframe)

            # create an action in the main windows menubar
            request_keyframe_action = QAction(str(keyframe.gps.timestamp))
            request_keyframe_action.triggered.connect(lambda: self.request_keyframe(keyframe))
            self.menu.addAction(request_keyframe_action)

        # if keyframe has sufficient data, apply camera calibration
        if keyframe.gps is not None and keyframe.image_point is not None and keyframe.intrinsics is None:
            intrinsics: IntrinsicCameraParameters
            extrinsics: ExtrinsicCameraParameters 
            intrinsics, extrinsics = determine_camera_parameters(keyframe, 1435)
            keyframe.intrinsics = intrinsics
            keyframe.extrinsics = extrinsics

        self.current_keyframe = keyframe
        self.keyframe_requested.emit(keyframe)
    

class SessionHandler(QObject):
    """ wrapper for dict able to read from json"""

    def __init__(self) -> None:
        super().__init__()
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

    def save_keyframes(self, keyframe_handler: KeyFrameHandler):
        """ saves key frame data to csv """
        creation_date_as_string = self.session_data.creation_date.strftime("%y-%m-%d_%X")
        path = f".\data\{creation_date_as_string}_keyframes.csv"
        with open(path, "w", encoding="ascii") as file:
            writer = csv.writer(file)

            writer.writerow({
                "timestamp",
                "altitude",
                "gradient",
                "focallength",
                "principallength",
                "swing",
                "tilt",
                "pan",
                "xoffset",
                "yoffset",
                "zoffset"
            })

            keyframe: KeyFrame
            for keyframe in keyframe_handler.data:
                writer.writerow([
                    keyframe.gps.timestamp,
                    keyframe.gps.altitude,
                    keyframe.gps.gradient,
                    keyframe.intrinsics.focal_length,
                    keyframe.intrinsics.principal_length,
                    keyframe.extrinsics.swing,
                    keyframe.extrinsics.tilt,
                    keyframe.extrinsics.pan,
                    keyframe.extrinsics.x_offset,
                    keyframe.extrinsics.y_offset,
                    keyframe.extrinsics.z_offset
                ])
