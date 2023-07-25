""" main window that uses all other windows in inheritance or instantiation """

import sys

from PySide6.QtWidgets import QApplication, QMainWindow#, QLabel
from initwin import filepicker
from navmap import gpsdata
from linechart import linechartplotter

class MainWindow(filepicker.FilePickerApp, QMainWindow):
    """ main window """

    def __init__(self):
        super().__init__()

    def open_video_dialog(self):
        _filename = super().open_video_dialog()

    def open_gps_data_dialog(self):
        _filename = super().open_gps_data_dialog()

        # Use file from dialog
        self.gpsdata = gpsdata.GPSData()
        _, data = self.gpsdata.read_csv_data(_filename)

        # open new window
        self.linechart_window = linechartplotter.LineChartApplication(
            [coordinate.timeid for coordinate in self.gpsdata.list_of_coords()],
            [coordinate.speed for coordinate in self.gpsdata.list_of_coords()],
            [coordinate.altitude for coordinate in self.gpsdata.list_of_coords()]
        )

        self.linechart_window.show()





if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    
    sys.exit(app.exec())