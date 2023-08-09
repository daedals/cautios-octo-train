"""
Window for displaying Linecharts
"""

# import sys
from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import QVBoxLayout, QWidget
import pyqtgraph as pg

from navmap import gpsdata

class COTLineChartWidget(QWidget):
    """ Line chart window specifically for speed and altitude against time """

    # signal when a point is clicked
    timestamp_requested = Signal(int)

    def __init__(self, _gps_data: gpsdata.GPSData):
        super().__init__()

        # Prepare data point
        speed_list = [coordinate.speed for coordinate in _gps_data.list_of_coords()]
        altitude_list = [coordinate.altitude for coordinate in _gps_data.list_of_coords()]
        self._time_list = [coordinate.timeid for coordinate in _gps_data.list_of_coords()]

        print(len(self._time_list), self._time_list[-1])

        # Set the application window title
        self.setWindowTitle("Line Chart Window "+ _gps_data.file_path.split("//")[-1])
        self.setToolTip(
            "Click on a data point to navigate to its time stamp.\n"+ 
            "The vertical line represents your position and may be dragged.\n"
            )

        # Create the main layout
        main_layout = QVBoxLayout()

        # Create two plot widgets for speed and altitude
        self.speed_plot = pg.PlotWidget(title="Speed vs. Time")
        self.altitude_plot = pg.PlotWidget(title="Altitude vs. Time")

        self.setLayout(main_layout)

        # Add the plot widgets to the main layout
        main_layout.addWidget(self.speed_plot)
        main_layout.addWidget(self.altitude_plot)

        # Set the horizontal range for both plots to display only 100 values
        self.speed_plot.setXRange(self._time_list[0] -50, self._time_list[-1] + 50)
        self.altitude_plot.setXRange(self._time_list[0] -50, self._time_list[-1] + 50)

        # Plot speed and altitude against time
        self.speed_curve = self.speed_plot.plot(pen='r')
        self.altitude_curve = self.altitude_plot.plot(pen='g')

        # Set the horizontal scaling of the plots to be the same
        self.speed_plot.setXLink(self.altitude_plot)

        # Update the plots with the provided data
        self.speed_curve.setData(self._time_list, speed_list)
        self.altitude_curve.setData(self._time_list, altitude_list)

        # Plot speed and altitude against time using ScatterPlotItem for individual points
        self.speed_scatter = pg.ScatterPlotItem(x=self._time_list, y=speed_list, pen='r', symbol='o', size=3, brush='r')
        self.altitude_scatter = pg.ScatterPlotItem(x=self._time_list, y=altitude_list, pen='g', symbol='o', size=3, brush='g')

        # Add the ScatterPlotItem to the plots
        self.speed_plot.addItem(self.speed_scatter)
        self.altitude_plot.addItem(self.altitude_scatter)

        # self.speed_scatter.setData(x=self._time_list, y=speed_list)
        # self.altitude_scatter.setData(x=self._time_list, y=altitude_list)

        # create vertical lines to indicate position
        self.speed_position_indicator = pg.InfiniteLine(0, angle= 90, bounds=[0, self._time_list[-1]])
        self.altitude_position_indicator = pg.InfiniteLine(0, angle= 90, bounds=[0, self._time_list[-1]])

        # add lines to plot
        self.speed_plot.addItem(self.speed_position_indicator)
        self.altitude_plot.addItem(self.altitude_position_indicator)

        # Connect the clicked signal of the ScatterPlotItem to handle interaction with data points
        self.speed_scatter.sigClicked.connect(self.on_point_clicked)
        self.altitude_scatter.sigClicked.connect(self.on_point_clicked)

        # self.timestamp_requested.connect(self.update_plot_on_frame_change)

    @Slot(list)
    def on_point_clicked(self, _, points):
        """ Slotted method for interaction with point """

        # Signal gives a list of at least one point, so we choose the middle one
        index = points[int(len(points)/2)].index()

        # Emit signal
        self.timestamp_requested.emit(self._time_list[index])

    @Slot(int)
    def update_plot_on_frame_change(self, timestamp: int):
        """ updates visuals when a new frame is displayed """
        self.speed_position_indicator.setPos(timestamp)
        self.altitude_position_indicator.setPos(timestamp)
