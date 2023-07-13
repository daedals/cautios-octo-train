import QtQuick
import QtQuick.Controls
import QtLocation 
import QtPositioning

ApplicationWindow {
    visible: false
    width: 800
    height: 600

    Plugin {
        id: osmPlugin
        name: "osm"
        PluginParameter {
            name: "osm.mapping.providersrepository.disabled"
            value: "true"
        }
        PluginParameter {
            name: "osm.mapping.providersrepository.address"
            value: "http://maps-redirect.qt.io/osm/5.6/"
        }
    }

    Map {
        id: map
        anchors.fill: parent
        plugin: osmPlugin
        center: QtPositioning.coordinate(5.000000, 5.000000)
        zoomLevel: 10

        MapQuickItem {
            id: markerItem
            anchorPoint.x: marker.width / 2
            anchorPoint.y: marker.height
            sourceItem: marker
            coordinate: QtPositioning.coordinate(5.000000, 5.000000)
        }

        Image {
            id: marker
            source: "./media/marker.png" // Path to your marker image
        }
    }
}