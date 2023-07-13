from PySide6.QtCore import Qt, QUrl, QObject
from PySide6.QtGui import QGuiApplication
from PySide6.QtPositioning import QGeoCoordinate, QGeoShape
from PySide6.QtLocation import QGeoServiceProvider
from PySide6.QtQml import QQmlApplicationEngine


def add_gps_data_points(map_object):
    # Create GPS data points
    gps_data_points = [
        QGeoCoordinate(51.5074, -0.1278),  # London
        QGeoCoordinate(40.7128, -74.0060),  # New York
        QGeoCoordinate(48.8566, 2.3522),  # Paris
        QGeoCoordinate(37.7749, -122.4194),  # San Francisco
    ]

    # Add data points to the map
    for coordinate in gps_data_points:
        shape = QGeoShape()
        shape.addCoordinate(coordinate)
        map_object.addMapItem(shape)


# Create the application instance
app = QGuiApplication([])

# Create the QML engine
engine = QQmlApplicationEngine()

# Create the GeoServiceProvider to access map data
service_provider = QGeoServiceProvider("osm")

# Check if the provider is valid
if service_provider.error() != QGeoServiceProvider.NoError:
    app.quit()

# Set the service provider for the application
# app.setGeoServiceProvider(service_provider)

# Load the QML file
engine.load(QUrl.fromLocalFile(".\data\map.qml"))

# Retrieve the root object from the QML file
root = engine.rootObjects()[0]

print(root)

# Retrieve the Map object from the QML file
map_object = root.findChild(QObject, "map")

# Check if the map object is valid
if map_object is not None:
    print("hi")
    # Add GPS data points to the map
    add_gps_data_points(map_object)

    # Show the map
    root.setProperty("visible", True)
else:
    print(":(")
    root.setProperty("visible", True)
    

# Run the application event loop
app.exec()