""" 
Marker item and marker model for adding a list of markers in the interactive map window
See: https://stackoverflow.com/questions/46429800/is-it-possible-to-create-mapquickitems-from-qml-in-python
"""

from random import random, randint

from PySide6.QtCore import Qt, QAbstractListModel, QByteArray, QModelIndex, QPointF # QVariant couldnt be imported
from PySide6.QtGui import QColor

class MarkerItem(object):
    """ CLass representing a Marker in QML """

    def __init__(self, position, color=QColor("red")):
        self._position = position
        self._color = color

    def position(self):
        """ getter for position """
        return self._position

    def setPosition(self, value):
        """ setter for position """
        self._position = value

    def color(self):
        """ getter for color """
        return self._color

    def setColor(self, value):
        """ setter for color """
        self._color = value


class MarkerModel(QAbstractListModel):
    """ Model for dynamically adding multiple markers """

    PositionRole = Qt.UserRole + 1
    ColorRole = Qt.UserRole + 2

    _roles = {PositionRole: QByteArray(b"markerPosition"), ColorRole: QByteArray(b"markerColor")}

    def __init__(self, parent=None):
        QAbstractListModel.__init__(self, parent)
        self._markers = []

    def rowCount(self, index=QModelIndex()):
        return len(self._markers)

    def roleNames(self):
        return self._roles

    def data(self, index, role=Qt.DisplayRole):
        if index.row() >= self.rowCount():
            return False #QVariant()
        marker = self._markers[index.row()]

        if role == MarkerModel.PositionRole:
            return marker.position()

        elif role == MarkerModel.ColorRole:
            return marker.color()

        return False #QVariant()

    def setData(self, index, value, role=Qt.EditRole):
        if index.isValid():
            marker = self._markers[index.row()]
            if role == MarkerModel.PositionRole:
                marker.setPosition(value)

            if role == MarkerModel.ColorRole:
                marker.setColor(value)

            self.dataChanged.emit(index, index)
            return True
        return QAbstractListModel.setData(self, index, value, role)

    def addMarker(self, marker):
        """"""
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        self._markers.append(marker)
        self.endInsertRows()

    def flags(self, index):
        """"""
        if not index.isValid():
            return Qt.ItemIsEnabled
        return QAbstractListModel.flags(index)|Qt.ItemIsEditable
