"""proof of concept for a window with an interactable map from a qml file"""

import sys
from PySide6.QtCore import QUrl, QObject, Signal, Slot, QPointF
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout

from PySide6.QtQuickWidgets import QQuickWidget

from tools.handler import GPSDataHandler
from gpswidgets.markermodel import MarkerModel


class InteractiveMapWindow(QWidget):

    def __init__(self, _gpsdata: GPSDataHandler):
        super().__init__()

        self.current_index = 0

        general_layout = QVBoxLayout()

        self.map_widget = QQuickWidget()

        print("Initialization started")

        print("Setting layout")
        general_layout.addWidget(self.map_widget)
        self.setLayout(general_layout)

        # self.engine = QQmlApplicationEngine()
        self.model = MarkerModel()
        self.model.point_clicked.connect(self.receive_clicked_signal)

        print("Adding markers to model")
        for i, coordinate in enumerate(_gpsdata.data):
            color = QColor(["red", "green"][i == self.current_index])
            self.model.addMarker(
                QPointF(coordinate.latitude, coordinate.longitude), color
                )

        print("Setting context property")
        self.map_widget.rootContext().setContextProperty("markerModel", self.model)

        # # Load the QML file
        print("Loading QML file")
        self.map_widget.setSource(QUrl.fromLocalFile(".\\train\\gpswidgets\\map.qml"))

        # # Retrieve the root object from the QML file
        # self.root = self.engine.rootObjects()[0]

        # # Create a Map Manager as backend object
        # self.map_manager = MapManager()

        # # Set mapmanager in qml file
        # self.root.setProperty("mapManager", self.map_manager)
        
        print("Initialization finished")

    @Slot(int, QPointF)
    def receive_clicked_signal(self, index, position: QPointF):
        """ Slot for markerModel's point_clicked signal"""
        self.model.setData(
            self.model.getIndexFromInt(self.current_index),
            QColor("red"),
            MarkerModel.ColorRole
            )
        self.model.setData(
            self.model.getIndexFromInt(index),
            QColor("green"),
            MarkerModel.ColorRole)
        self.current_index = index
        # hi = self.model.data(self.model.getIndexFromInt(index), self.model.PositionRole)
        print(f"Signal received from marker {index} at {position.x()}, {position.y()}")


if __name__ == '__main__':
    main()


def main():
    # prepare GPS data
    gpsdata = GPSDataHandler()
    file_path = './data/gps_spring.csv'
    # header, data = gpsdata.read_csv_data(file_path)

    # # Create the application instance
    # app = QGuiApplication([])

    # # Create the QML engine
    # engine = QQmlApplicationEngine()
    # engine.quit.connect(app.quit)

    # model = MarkerModel()

    # for coordinate in gpsdata.data:
    #     model.addMarker(MarkerItem(QPointF(coordinate.latitude, coordinate.longitude), QColor("red")))

    # engine.rootContext().setContextProperty('markerModel', model)

    # # Load the QML file
    # engine.load(QUrl.fromLocalFile(".\\train\\gpswidgets\\map.qml"))

    # # Retrieve the root object from the QML file
    # root = engine.rootObjects()[0]

    # # Create a Map Manager as backend object
    # map_manager = MapManager()

    # # Set mapmanager in qml file
    # root.setProperty("mapManager", map_manager)

    app = QApplication()
    gpsdata.read_csv_data(file_path)
    w = InteractiveMapWindow(gpsdata)
    w.show()

    sys.exit(app.exec())
    
