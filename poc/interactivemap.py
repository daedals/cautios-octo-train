"""proof of concept for a window with an interactable map from a qml file"""

import sys
from PySide6.QtCore import QUrl, QObject, Signal
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

from gpsdata import GPSData
from markermodel import MarkerModel, MarkerItem

class MapManager(QObject):
    """Dummy class for communication with qml file"""

    # Signal can be slotted in qml with function called onMarkerRequest
    markerRequest = Signal(float, float)

    def request_marker(self, _lat: float, _lon: float):
        """Emits a custom signal to request marker placement on the map"""
        self.markerRequest.emit(_lat, _lon)


    def add_gps_data_points(self, _gpsdata: GPSData): #, _map_object):
        """adds gps data points to a map object"""

        # Add data points to the map
        for coordinate in _gpsdata.list_of_coords():
            # request a marker placement
            self.request_marker(coordinate.latitude(), coordinate.longitude())
            break


if __name__ == '__main__':
    import sys

    # Create the application instance
    app = QGuiApplication([])

    # Create the QML engine
    engine = QQmlApplicationEngine()
    engine.quit.connect(app.quit)

    # # Create the GeoServiceProvider to access map data
    # service_provider = QGeoServiceProvider("osm")

    # # Check if the provider is valid
    # if service_provider.error() != QGeoServiceProvider.NoError:
    #     app.quit()

    # Set the service provider for the application
    # app.setGeoServiceProvider(service_provider)

    from PySide6.QtCore import QPointF
    from PySide6.QtGui import QColor

    gpsdata = GPSData()
    file_path = './data/gps_spring.csv'
    header, data = gpsdata.read_csv_data(file_path)

    model = MarkerModel()

    i = 10000
    for coordinate in gpsdata.data:
        i -= 1
        if i%2: 
            continue
        model.addMarker(MarkerItem(QPointF(coordinate.latitude(), coordinate.longitude()), QColor("red")))
        # if i < 0:
        #     break

    engine.rootContext().setContextProperty('markerModel', model)

    # Load the QML file
    engine.load(QUrl.fromLocalFile(".\\data\\map.qml"))

    # Retrieve the root object from the QML file
    root = engine.rootObjects()[0]

    # Create a Map Manager as backend object
    map_manager = MapManager()

    # Set mapmanager in qml file
    root.setProperty("mapManager", map_manager)




    sys.exit(app.exec())
