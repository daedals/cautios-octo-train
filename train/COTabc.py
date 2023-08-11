""" Intrdoduces different abstract base classes:

AbstractBaseWidget
AbstractBaseHandler
"""

from abc import ABC, abstractmethod

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Signal, Slot
# from PySide6.QtGui import 

from COTdataclasses import GPSDatum, KeyFrame, SessionData
from tools.handler import GPSDataHandler, SessionHandler, KeyFrameHandler

class AbstractBaseWidget(ABC):
    """ abstract base class for every widget that is utilized """

    def initialize(self, session_handler: SessionHandler, gpsdata_handler: GPSDataHandler, keyframe_handler: KeyFrameHandler):
        
        self._session_handler = session_handler
        self._gpsdata_handler = gpsdata_handler
        self._keyframe_handler = keyframe_handler

        self._gpsdata_handler.gpsdatum_requested.connect(
            self._react_to_gpsdatum_change
        )
        self._keyframe_handler.keyframe_requested.connect(
            self._react_to_keyframe_change
        )

        self._widget: QWidget = QWidget()

        self._initialize()
        self._setup_ui()

    def show(self):
        """ Wrapper for widgets show method """
        self._widget.show()

    def close(self) -> bool:
        """ wrapper for widgets close method """
        return self._widget.close()

    @abstractmethod
    def _setup_ui(self):
        """ _func for ui setup  """
        raise NotImplementedError(
            "Should implement"
        )

    @abstractmethod
    def _initialize(self):
        """ _func for data setup  """
        raise NotImplementedError(
            "Should implement"
        )

    @Slot(KeyFrame)
    def _react_to_keyframe_change(self, keyframe: KeyFrame):
        self.react_to_keyframe_change(keyframe)

    @abstractmethod
    def react_to_keyframe_change(self, keyframe: KeyFrame):
        """ _slot for a reaction to a change in keyframes  """
        raise NotImplementedError(
            "Should implement"
        )

    @Slot(GPSDatum)
    def _react_to_gpsdatum_change(self, gpsdatum: GPSDatum):
        keyframe = self._keyframe_handler.from_gpsdatum(gpsdatum)
        if keyframe is not None:
            self.react_to_keyframe_change(keyframe)
        else:
            self.react_to_gpsdatum_change(gpsdatum)
    
    @abstractmethod
    def react_to_gpsdatum_change(self, gpsdatum: GPSDatum):
        """ _slot for a reaction to a change in gpsdata """
        raise NotImplementedError(
            "Should implement"
        )

class AbstractBaseHandler(ABC):
    """ abstract base class for every handler """