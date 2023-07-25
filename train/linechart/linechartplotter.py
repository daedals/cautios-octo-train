"""
Window for displaying Linecharts
"""

# import sys
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QVBoxLayout, QWidget
import pyqtgraph as pg


class LineChartApplication(QWidget):
    """ Line chart window specifically for speed and altitude against time """

    # signal when a point is clicked
    scatterPointClicked = Signal(int)

    def __init__(self, time_list, speed_list, altitude_list):
        super().__init__()

        self.time_list = time_list

        # Set the application window title
        self.setWindowTitle("Line Chart Application")

        # Create the main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)

        # Create two plot widgets for speed and altitude
        self.speed_plot = pg.PlotWidget(title="Speed vs. Time")
        self.altitude_plot = pg.PlotWidget(title="Altitude vs. Time")

        # Add the plot widgets to the main layout
        main_layout.addWidget(self.speed_plot)
        main_layout.addWidget(self.altitude_plot)

        # Set the main widget
        self.setCentralWidget(main_widget)

        # Set the horizontal range for both plots to display only 100 values
        self.speed_plot.setXRange(time_list[0] -50, time_list[-1] + 50)
        self.altitude_plot.setXRange(time_list[0] -50, time_list[-1] + 50)

        # Plot speed and altitude against time
        self.speed_curve = self.speed_plot.plot(pen='b')
        self.altitude_curve = self.altitude_plot.plot(pen='g')

        # Set the horizontal scaling of the plots to be the same
        self.speed_plot.setXLink(self.altitude_plot)

        # Update the plots with the provided data
        self.speed_curve.setData(time_list, speed_list)
        self.altitude_curve.setData(time_list, altitude_list)

        # Plot speed and altitude against time using ScatterPlotItem for individual points
        self.speed_scatter = pg.ScatterPlotItem(x=time_list, y=speed_list, pen='b', symbol='o', size=8, brush='b')
        self.altitude_scatter = pg.ScatterPlotItem(x=time_list, y=altitude_list, pen='g', symbol='o', size=8, brush='g')

        # Add the ScatterPlotItem to the plots
        self.speed_plot.addItem(self.speed_scatter)
        self.altitude_plot.addItem(self.altitude_scatter)

        self.speed_scatter.setData(x=time_list, y=speed_list)
        self.altitude_scatter.setData(x=time_list, y=altitude_list)

        # Connect the clicked signal of the ScatterPlotItem to handle interaction with data points
        self.speed_scatter.sigClicked.connect(self.on_point_clicked)
        self.altitude_scatter.sigClicked.connect(self.on_point_clicked)

    def on_point_clicked(self, _, points):
        """ Slotted method for interaction with point """

        # Get the index of the clicked data point (middle)
        index = points[int(len(points)/2)].index()

        # Print the corresponding time value to the console
        print(f"Time value of clicked data point: {self.time_list[index]} ({index})")

        # Emit signal
        self.scatterPointClicked.emit(index)
