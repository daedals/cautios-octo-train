""" Collection of all used Dataclasses in this project and some additional functionailty regarding those



"""

from dataclasses import dataclass
from datetime import datetime, time

from PySide6.QtCore import QPointF
from PySide6.QtGui import QPixmap

@dataclass
class SessionData:
    """ data container containing relevant session data """
    video_file_path: str
    gps_file_path: str
    image_width: int
    image_height: int
    creation_date: datetime = datetime.now()

@dataclass
class GPSDatum:
    """ data container containing data as to the header of the given csv files """
    # actual time of recording
    timeid: time
    # time in seconds from start
    timestamp: int
    # coordinates as decimal degrees
    latitude: float
    longitude: float
    # speed in km/h
    speed: float
    # course is not used
    course: int
    # altitude in meters above 0
    altitude: float

    def __eq__(self, other):
        if not isinstance(other, GPSDatum):
            return NotImplemented
        return self.timestamp == other.timestamp

@dataclass
class LocationDatum:
    """ location with camera offset x, y, z relative to optical axis' intersection with world X-Y plane"""
    x_offset: float
    y_offset: float
    z_offset: float

@dataclass
class OrientationDatum:
    """ camera orientation with swing, tilt and pan """
    swing: float
    tilt: float
    pan: float

@dataclass
class ExtrinsicCameraParameters(LocationDatum, OrientationDatum):
    """ extrinsic camera parameters """

@dataclass
class IntrinsicCameraParameters:
    """ intrinsic camera parameters """
    # distance of camera to image plane
    focal_length: float
    # distance from image plane to reference world x-y-plane
    principal_length: float

@dataclass
class ImagePointContainer:
    """ just conviniently stores 4 image points """
    A: list
    B: list
    C: list
    D: list

    def to_list(self) -> list:
        return [self.A, self.B, self.C, self.D]

@dataclass
class KeyFrame:
    """ data container containing relevant keyframe data """
    gps: GPSDatum
    pixmap: QPixmap
    image_point: ImagePointContainer
    intrinsics: IntrinsicCameraParameters
    extrinsics: ExtrinsicCameraParameters

    def __eq__(self, other):
        if not isinstance(other, KeyFrame):
            return NotImplemented
        return self.gps.timestamp == other.gps.timestamp