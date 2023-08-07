
import QtQuick
import QtQuick.Controls
import QtLocation
import QtPositioning

Rectangle {
    id: window
    width: 800
    height: 600
    visible: true
    property int marker_size: 8

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

    Map {
        id: mapItem
        // activeMapType: supportedMapTypes[0] // StreetMap
        // activeMapType: supportedMapTypes[0] // Cycle Map
        activeMapType: supportedMapTypes[0] // Transit Map
        // activeMapType: supportedMapTypes[0] // Night Transit Map
        // activeMapType: supportedMapTypes[0] // Terrain Map
        // activeMapType: supportedMapTypes[0] // Hiking Map

        anchors.fill: parent
        plugin: osmPlugin
        center: QtPositioning.coordinate(63.43674 ,10.40070)
        zoomLevel: 14

        // this is only to show supported map types for design purposes
        // onSupportedMapTypesChanged: {
        //     console.log("Supported MapType:");
        //     for (var i = 0; i < mapItem.supportedMapTypes.length; i++) {
        //         console.log(i, supportedMapTypes[i].name);
        //     }
        // }

        // map item view, initialized in interactive map using mapmarkers.py
        MapItemView {
            model: markerModel
            delegate: MapQuickItem{
                anchorPoint: Qt.point(2.5, 2.5)
                coordinate: QtPositioning.coordinate(markerPosition.x, markerPosition.y)
                zoomLevel: 0
                sourceItem: Rectangle{
                    width:  marker_size
                    height: marker_size
                    radius: marker_size/2
                    // border.color: "white"
                    color: markerColor
                    // border.width: 1
                    MouseArea{
                        anchors.fill: parent
                        onClicked: {
                            // console.log("MapQuickItem clicked")
                            markerModel.forward_clicked_signal(markerIndex, markerPosition)
                        }
                    }
                }
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
}
