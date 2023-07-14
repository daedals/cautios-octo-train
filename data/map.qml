


import QtQuick
import QtQuick.Controls
import QtLocation
import QtPositioning

ApplicationWindow {
    id: window
    width: 800
    height: 600
    visible: true
    title: "GPS Data"

    property QtObject mapManager

    Plugin {
        id: osmPlugin
        name: "osm"

        // workaround for following Error:
        // QGeoTileProviderOsm: Tileserver disabled at  QUrl("http://maps-redirect.qt.io/osm/5.8/satellite")
        // QGeoTileFetcherOsm: all providers resolved
        // qt.network.ssl: QSslSocket::connectToHostEncrypted: TLS initialization failed
        // found at https://forum.qt.io/topic/118089/error-when-running-minimal-map-example
        PluginParameter {
            name: "osm.mapping.providersrepository.disabled"
            value: "true"
        }
        PluginParameter {
            name: "osm.mapping.providersrepository.address"
            value: "http://maps-redirect.qt.io/osm/5.6/"
        }
    }

    function addMarker(latitude, longitude)
    {
        var Component = Qt.createComponent(".\\media\\marker.png")
        var item = Component.createObject(window, {
                                              coordinate: QtPositioning.coordinate(latitude, longitude)
                                          })
        map.addMapItem(item)
    }

    Map {
        id: mapItem
        activeMapType: supportedMapTypes[0]

        anchors.fill: parent
        plugin: osmPlugin
        center: QtPositioning.coordinate(63.43674 ,10.40070)
        zoomLevel: 14

        onSupportedMapTypesChanged: {
            console.log("Supported MapType:");
            for (var i = 0; i < mapItem.supportedMapTypes.length; i++) {
                console.log(i, supportedMapTypes[i].name);
            }
        }

        property geoCoordinate startCentroid

        PinchHandler {
            id: pinch
            target: null
            onActiveChanged: if (active) {
                mapItem.startCentroid = mapItem.toCoordinate(pinch.centroid.position, false)
            }
            onScaleChanged: (delta) => {
                mapItem.zoomLevel += Math.log2(delta)
                mapItem.alignCoordinateToPoint(mapItem.startCentroid, pinch.centroid.position)
            }
            onRotationChanged: (delta) => {
                mapItem.bearing -= delta
                mapItem.alignCoordinateToPoint(mapItem.startCentroid, pinch.centroid.position)
            }
            grabPermissions: PointerHandler.TakeOverForbidden
        }
        WheelHandler {
            id: wheel
            // workaround for QTBUG-87646 / QTBUG-112394 / QTBUG-112432:
            // Magic Mouse pretends to be a trackpad but doesn't work with PinchHandler
            // and we don't yet distinguish mice and trackpads on Wayland either
            acceptedDevices: Qt.platform.pluginName === "cocoa" || Qt.platform.pluginName === "wayland"
                             ? PointerDevice.Mouse | PointerDevice.TouchPad
                             : PointerDevice.Mouse
            rotationScale: 1/120
            property: "zoomLevel"
        }
        DragHandler {
            id: drag
            target: null
            onTranslationChanged: (delta) => mapItem.pan(-delta.x, -delta.y)
        }
        Shortcut {
            enabled: mapItem.zoomLevel < mapItem.maximumZoomLevel
            sequence: StandardKey.ZoomIn
            onActivated: mapItem.zoomLevel = Math.round(mapItem.zoomLevel + 1)
        }
        Shortcut {
            enabled: mapItem.zoomLevel > mapItem.minimumZoomLevel
            sequence: StandardKey.ZoomOut
            onActivated: mapItem.zoomLevel = Math.round(mapItem.zoomLevel - 1)
        }
    }

    Connections {
        target: mapManager
        function onMarkerRequest(lat, lon) { console.log(lat, lon) }
    }
}
