""" main window that uses all other windows in inheritance or instantiation """

import sys

# from Pyside6.QtCore import 
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QApplication, QMainWindow

from initwin import filepicker, sessionrestore
from navmap import gpsdata, linechartplotter


class MainWindow(QMainWindow):
    """ main window """

    def __init__(self):
        super().__init__()

        # menubar creation for filepicker
        menubar = self.menuBar()

        # Component setup
        self._gps_data: gpsdata.GPSData() = gpsdata.GPSData()
        self._linechart_window : linechartplotter.LineChartApplication = None

        self.session = sessionrestore.Session()
        self.filepicker = filepicker.FilePickerWidget(self.session, menubar)

        # UI setup
        self.setWindowTitle("Main Window (Exit all on close)")


        # connect window initialization to filepickers import signal
        self.filepicker.importRequested.connect(self.initialize)

        self.setCentralWidget(self.filepicker)

    def initialize(self):
        """ initialize data and windows, if already initialized show windows if closed """

        self._gps_data.read_csv_data(self.filepicker.gps_data_path)

        self.initialize_linechart_window()
        self.initialize_interactive_map()

    def initialize_linechart_window(self):
        """ initialization of the linechart window"""
        if self._linechart_window is not None:
            self._linechart_window.close()
            self._linechart_window = None
            
        self._linechart_window = linechartplotter.LineChartApplication(self._gps_data)
        self._linechart_window.show()

    def initialize_interactive_map(self):
        pass

    def initialize_datadisplay(self):
        pass

    def initialize_videoplayer(self):
        pass

    def cleanup(self):
        """ cleanup to be called at closeEvent """
        if self._linechart_window is not None:
            self._linechart_window.close()
            self._linechart_window = None


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