""" main window that uses all other components in inheritance or instantiation """

import sys

from PySide6.QtWidgets import QApplication, QMainWindow, QLabel
from PySide6.QtCore import Slot, Signal
from PySide6.QtGui import QCloseEvent, QPixmap

from COTdataclasses import KeyFrame, GPSDatum
from initwin import filepicker, sessionrestore
from navmap import gpsdata, linechartplotter
from videopl import videoplayer
from imagedit import imageeditor


class MainWindow(QMainWindow):
    """ main window """

    def __init__(self):
        super().__init__()

        # menubar creation for filepicker
        menubar = self.menuBar()

        # Component setup
        self._gpsdata: gpsdata.GPSData() = gpsdata.GPSData()
        self.session = sessionrestore.Session()
        self.filepicker = filepicker.FilePickerWidget(self.session, menubar)

        self._linechart_window : linechartplotter.COTLineChartWidget = None
        self._videoplayer_window : videoplayer.VideoPlayerWidget = None

        self.active_windows = []

        # UI setup
        self.setWindowTitle("Main Window (Exit all on close)")

        # connect window initialization to filepickers import signal
        self.filepicker.importRequested.connect(self.initialize)

        self.setCentralWidget(self.filepicker)

    def initialize(self):
        """ initialize data and windows, if already initialized show windows if closed """

        self._gpsdata.read_csv_data(self.filepicker.gps_data_path)

        self.initialize_linechart_window()
        self.initialize_interactive_map()
        self.initialize_videoplayer()

        self.connect_signals()

    def initialize_linechart_window(self):
        """ initialization of the linechart window"""
        if self._linechart_window is not None:
            self._linechart_window.close()
            self.active_windows.remove(self._linechart_window)
            self._linechart_window = None

        self._linechart_window = linechartplotter.COTLineChartWidget(self._gpsdata)
        self.active_windows.append(self._linechart_window)
        self._linechart_window.show()

    def initialize_interactive_map(self):
        pass

    def initialize_datadisplay(self):
        pass

    def initialize_videoplayer(self):
        """ initialization of the video player window """
        if self._videoplayer_window is not None:
            self._videoplayer_window.close()
            self.active_windows.remove(self._videoplayer_window)
            self._linechart_window = None

        self._videoplayer_window = videoplayer.VideoPlayerWidget()
        self._videoplayer_window.load_video(
            self.filepicker.video_path,
            self._gpsdata
            )
        self.active_windows.append(self._videoplayer_window)
        self._videoplayer_window.show()

    def connect_signals(self):
        """ connect all nessecary signals after all windows have been created """
        self._videoplayer_window.frame_export_requested.connect(self.open_image_editor)
        self._videoplayer_window.frame_export_requested.connect(
            self._linechart_window.add_keyframe
        )
        self._videoplayer_window.frame_updated.connect(
            self._linechart_window.update_plot_on_frame_change
        )

        self._linechart_window.timestamp_requested.connect(self._videoplayer_window.set_frame_by_timestamp)


    @Slot(QPixmap)
    def open_image_editor(self, pixmap: QPixmap):
        """ slot for export signal from _video_player_window, opens image in new window """
        self._image_editor_window = imageeditor.ImageViewerWidget(pixmap)
        self._image_editor_window.show()


    def cleanup(self):
        """ cleanup to be called at closeEvent """
        for window in self.active_windows:
            if window is not None:
                window.close()
                window = None

    def closeEvent(self, event: QCloseEvent) -> None:
        """ extend innate closeEvent to cleanup windows """
        self.cleanup()
        self.session.save()

        return super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    
    sys.exit(app.exec())