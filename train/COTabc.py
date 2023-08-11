""" Intrdoduces an abstract base class for all windows and widgets of cot to follow """

import abc
from typing import Optional

from PySide6.QtWidgets import QWidget, QMenuBar
from PySide6.QtCore import Signal, Slot
# from PySide6.QtGui import 

from COTdataclasses import KeyFrame, SessionData
from tools.handler import GPSDataHandler, SessionHandler, KeyFrameHandler

class AbstractBaseWidget(QWidget, abc.ABC):
    """ abstract base class """

    def initialize(self, menubar: QMenuBar, gpsdata_handler: GPSDataHandler, session_handler: SessionHandler, keyframe_handler: KeyFrameHandler):
        
        self._gpsdata_handler = gpsdata_handler
        self._session_handler = session_handler
        self._keyframe_handler = keyframe_handler

        self._initialize()
        self._setup_ui(menubar)

    @abc.abstractmethod
    def _setup_ui(self, menubar: QMenuBar):
        """ _func for ui setup  """
        raise NotImplementedError(
            "Should implement _setup_ui()"
        )

    @abc.abstractmethod
    def _initialize(self):
        """ _func for data setup  """
        raise NotImplementedError(
            "Should implement _initialize()"
        )

    @Slot(KeyFrame)
    @abc.abstractmethod
    def react_to_key_frame_change(self, keyframe: KeyFrame):
        pass