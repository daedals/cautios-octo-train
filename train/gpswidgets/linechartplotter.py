"""
Window for displaying Linecharts
"""

# import sys
from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import QMenuBar, QVBoxLayout, QWidget

import pyqtgraph as pg

from COTdataclasses import GPSDatum, KeyFrame
from COTabc import AbstractBaseWidget
from tools.handler import GPSDataHandler, SessionHandler, KeyFrameHandler

class COTLineChartWidget(AbstractBaseWidget):
    """ Line chart window specifically for speed and altitude against time """

    ################################## Implementation of abstract methods ###########################################
    def _initialize(self):
        # Create two plot widgets for speed and altitude
        self.speed_plot = pg.PlotWidget(title="Speed vs. Time")
        self.altitude_plot = pg.PlotWidget(title="Altitude vs. Time")
        self.gradient_plot = pg.PlotWidget(title="Gradient vs. Time")

        # Prepare data points
        speed_list = [gpsdatum.speed for gpsdatum in self._gpsdata_handler.list_data()]
        altitude_list = [gpsdatum.altitude for gpsdatum in self._gpsdata_handler.list_data()]
        gradient_list = [gpsdatum.gradient for gpsdatum in self._gpsdata_handler.list_data()]
        time_list = [gpsdatum.timestamp for gpsdatum in self._gpsdata_handler.list_data()]
        
        # Set the horizontal range for both plots to display only 100 values
        self.speed_plot.setXRange(time_list[0] -50, time_list[-1] + 50)
        self.altitude_plot.setXRange(time_list[0] -50, time_list[-1] + 50)
        self.gradient_plot.setXRange(time_list[0] -50, time_list[-1] + 50)

        # Plot speed and altitude against time
        self.speed_curve = self.speed_plot.plot(pen='g')
        self.altitude_curve = self.altitude_plot.plot(pen='g')
        self.gradient_curve = self.gradient_plot.plot(pen='g')

        # Set the horizontal scaling of the plots to be the same
        self.speed_plot.setXLink(self.altitude_plot)
        self.gradient_plot.setXLink(self.altitude_plot)

        # Update the plots with the provided data
        self.speed_curve.setData(time_list, speed_list)
        self.altitude_curve.setData(time_list, altitude_list)
        self.gradient_curve.setData(time_list, gradient_list)

        # Plot speed and altitude against time using ScatterPlotItem for individual points
        self.speed_scatter = pg.ScatterPlotItem(x=time_list, y=speed_list, pen='g', symbol='o', size=2, brush='g')
        self.altitude_scatter = pg.ScatterPlotItem(x=time_list, y=altitude_list, pen='g', symbol='o', size=2, brush='g')
        self.gradient_scatter = pg.ScatterPlotItem(x=time_list, y=gradient_list, pen='g', symbol='o', size=2, brush='g')

        # Add the ScatterPlotItem to the plots
        self.speed_plot.addItem(self.speed_scatter)
        self.altitude_plot.addItem(self.altitude_scatter)
        self.gradient_plot.addItem(self.gradient_scatter)

        # create vertical lines to indicate position
        self.speed_position_indicator = pg.InfiniteLine(0, angle= 90, bounds=[0, time_list[-1]])
        self.altitude_position_indicator = pg.InfiniteLine(0, angle= 90, bounds=[0, time_list[-1]])
        self.gradient_position_indicator = pg.InfiniteLine(0, angle= 90, bounds=[0, time_list[-1]])

        # add lines to plot
        self.speed_plot.addItem(self.speed_position_indicator)
        self.altitude_plot.addItem(self.altitude_position_indicator)
        self.gradient_plot.addItem(self.gradient_position_indicator)

        # Connect the clicked signal of the ScatterPlotItem to handle interaction with data points
        self.speed_scatter.sigClicked.connect(self.on_point_clicked)
        self.altitude_scatter.sigClicked.connect(self.on_point_clicked)
        self.gradient_scatter.sigClicked.connect(self.on_point_clicked)
        
        self._keyframes = []
        self._keyframe_indicators = []

    def _setup_ui(self):
        # Set the application window title and general tooltip
        self._widget.setWindowTitle("Line Chart Window "+ self._gpsdata_handler.file_path.split("/")[-1])
        self._widget.setToolTip(
            "Click on a data point to navigate to its timestamp.\n"+ 
            "The yellow vertical line represents your position.\n"+
            "Blue vertical lines represent keyframes."
        )

        # Create the main layout
        main_layout = QVBoxLayout()

        # Add the plot widgets to the main layout
        main_layout.addWidget(self.speed_plot)
        main_layout.addWidget(self.altitude_plot)
        main_layout.addWidget(self.gradient_plot)

        # set layout
        self._widget.setLayout(main_layout)

    def react_to_keyframe_change(self, keyframe: KeyFrame):
        # add a vertical line as an indicator for a keyframe
        self._keyframes.append(keyframe)
        speed_keyframe_indicator = pg.InfiniteLine(keyframe.gps.timestamp, angle= 90, movable=False, pen="b")
        altitude_keyframe_indicator = pg.InfiniteLine(keyframe.gps.timestamp, angle= 90, movable=False, pen="b")
        gradient_keyframe_indicator = pg.InfiniteLine(keyframe.gps.timestamp, angle= 90, movable=False, pen="b")

        self.speed_plot.addItem(speed_keyframe_indicator)
        self.altitude_plot.addItem(altitude_keyframe_indicator)
        self.gradient_plot.addItem(gradient_keyframe_indicator)

        self._keyframe_indicators.append(
            [speed_keyframe_indicator, altitude_keyframe_indicator, gradient_keyframe_indicator]
        )

        # update position indicators
        self.speed_position_indicator.setPos(keyframe.gps.timestamp)
        self.altitude_position_indicator.setPos(keyframe.gps.timestamp)
        self.gradient_position_indicator.setPos(keyframe.gps.timestamp)

    def react_to_gpsdatum_change(self, gpsdatum: GPSDatum):
        """ updates visuals when a new frame is displayed """
        self.speed_position_indicator.setPos(gpsdatum.timestamp)
        self.altitude_position_indicator.setPos(gpsdatum.timestamp)
        self.gradient_position_indicator.setPos(gpsdatum.timestamp)


    ################################## Implementation of class methods ###########################################

    @Slot(list)
    def on_point_clicked(self, _, points):
        """ Slotted method for interaction with point """

        # Signal gives a list of at least one point, so we choose the middle one
        index = points[int(len(points)/2)].index()

        # request datum from handler
        self._gpsdata_handler.request_gpsdatum(self._gpsdata_handler[index])

    @Slot(GPSDatum)
    def update_plot_on_frame_change(self, gpsdatum: GPSDatum):
        """ updates visuals when a new frame is displayed """
        self.speed_position_indicator.setPos(gpsdatum.timestamp)
        self.altitude_position_indicator.setPos(gpsdatum.timestamp)
        self.gradient_position_indicator.setPos(gpsdatum.timestamp)
