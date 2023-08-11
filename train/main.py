""" main window that uses all other components in inheritance or instantiation """

import sys

from PySide6.QtWidgets import QApplication, QMainWindow, QMenuBar
from PySide6.QtCore import Slot, Signal
from PySide6.QtGui import QCloseEvent

from tools.handler import GPSDataHandler, SessionHandler, KeyFrameHandler

from datawidgets.filepicker import FilePickerWidget
from datawidgets.dataview import DataViewWidget

from gpswidgets.linechartplotter import COTLineChartWidget

from imgwidgets.imageeditor import ImageViewerWidget
from imgwidgets.videoplayer import VideoPlayerWidget


class MainWindow(QMainWindow):
    """ main window """

    def __init__(self):
        super().__init__()

        # create menubar for widget initialization
        menubar: QMenuBar = self.menuBar()

        # create handler
        self._session_handler: SessionHandler = SessionHandler()
        self._filepicker = FilePickerWidget(self._session_handler, menubar)
        self._gpsdata_handler: GPSDataHandler = GPSDataHandler()
        self._keyframe_handler: KeyFrameHandler = KeyFrameHandler(menubar)


        self._linechart_window: COTLineChartWidget = COTLineChartWidget()
        self._videoplayer_window: VideoPlayerWidget = VideoPlayerWidget()
        self._image_editor_window: ImageViewerWidget = ImageViewerWidget()
        self._dataview_window: DataViewWidget = DataViewWidget()

        self.active_windows = [
            self._linechart_window,
            self._videoplayer_window,
            self._image_editor_window,
            self._dataview_window
        ]

        # UI setup
        self.setWindowTitle("Main Window (Exit all on close)")

        # connect window initialization to filepickers import signal
        self._filepicker.import_requested.connect(self.initialize)

        self.setCentralWidget(self._filepicker)

    def initialize(self):
        """ initialize data and windows, if already initialized show windows if closed """

        self._gpsdata_handler.read_csv_data(self._filepicker.gps_data_path)

        self._linechart_window.initialize(
            self._session_handler,
            self._gpsdata_handler,
            self._keyframe_handler
        )
        self._linechart_window.show()

        self._videoplayer_window.initialize(
            self._session_handler,
            self._gpsdata_handler,
            self._keyframe_handler
        )
        self._videoplayer_window.show()

        self._image_editor_window.initialize(
            self._session_handler,
            self._gpsdata_handler,
            self._keyframe_handler
        )
        # don't show, shows itself, when first keyframe is exported

        self._dataview_window.initialize(
            self._session_handler,
            self._gpsdata_handler,
            self._keyframe_handler
        )
        self._dataview_window.show()



    def cleanup(self):
        """ cleanup to be called at closeEvent """
        for window in self.active_windows:
            if window is not None:
                window.close()
                window = None

    def closeEvent(self, event: QCloseEvent) -> None:
        """ extend innate closeEvent to cleanup windows """
        self.cleanup()
        self._session_handler.save()

        return super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    
    sys.exit(app.exec())