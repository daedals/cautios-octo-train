""" main window that uses all other windows in inheritance or instantiation """

import sys

# from Pyside6.QtCore import 
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QApplication, QMainWindow

from initwin import filepicker, sessionrestore
from navmap import gpsdata, linechartplotter


class MainWindow(QMainWindow):
    """ main window """

    _gps_data: gpsdata.GPSData() = None
    _linechart_window : linechartplotter.LineChartApplication = None

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Main Window (Exit all on close)")

        menubar = self.menuBar()

        self.session = sessionrestore.Session()
        self.filepicker = filepicker.FilePickerWidget(self.session, menubar)

        # connect window initialization to filepickers import signal
        self.filepicker.importRequested.connect(self.initialize)

        self.setCentralWidget(self.filepicker)

    def initialize(self):
        """ initialize data and windows, if already initialized show windows if closed """

        # Prepare gps data if there is none or its new
        if self._gps_data is None or self.filepicker.gps_data_path.lower() != self._gps_data.file_path.lower():
            self._gps_data = gpsdata.GPSData()
            self._gps_data.read_csv_data(self.filepicker.gps_data_path)

            # if new gps data is supplied and there is already an active linechart window, close it and discard the reference
            if self._linechart_window is not None:
                self._linechart_window.close()
                self._linechart_window = None


        # Use gps data to open new window if it hasnt been created
        if self._linechart_window is None:
            self._linechart_window = linechartplotter.LineChartApplication(self._gps_data)

        self._linechart_window.show()

    def closeEvent(self, event: QCloseEvent) -> None:
        """ extend innate closeEvent to cleanup windows """
        if self._linechart_window is not None:
            self._linechart_window.close()
            self._linechart_window = None

        self.session.save()

        return super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    
    sys.exit(app.exec())