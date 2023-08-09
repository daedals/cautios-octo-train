""" Collection of all used Dataclasses in this project and some additional functionailty regarding those



"""

from dataclasses import dataclass
from datetime import datetime, time

from PySide6.QtCore import QPointF
from PySide6.QtGui import QPixmap

@dataclass
class SessionData:
    """ data container containing relevant session data """
    creation_date: datetime = datetime.now()
    video_file_path: str
    gps_file_path: str

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

@dataclass
class KeyFrame:
    """ data container containing relevant keyframe data """
    gpsdata: GPSDatum
    pixmap: QPixmap

@dataclass
class LocationDatum:
    """ location with relativ x, y, z """
    x: float
    y: float
    z: float

@dataclass
class OrientationDatum:
    """ orientation with pitch, ywa and roll """
    x: float
    y: float
    z: float

@dataclass
class ExtrinsicCameraParameters:
    """ extrinsic camera parameters """
    location: LocationDatum
    orientation: OrientationDatum

@dataclass
class IntrinsicCameraParameters:
    """ intrinsic camera parameters """
    focal_length: float
    principal_point: QPointF
    image_width: int
    image_height: int
