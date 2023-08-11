""" 
Marker item and marker model for adding a list of markers in the interactive map window
See: https://stackoverflow.com/questions/46429800/is-it-possible-to-create-mapquickitems-from-qml-in-python
"""

from PySide6.QtCore import Qt, QAbstractListModel, QByteArray, QModelIndex, QPointF, Slot, Signal
from PySide6.QtGui import QColor

class MarkerItem(object):
    """ Class representing a Marker in QML """

    def __init__(self, index, position: QPointF, color= QColor("red")):
        self._index = index
        self._position = position
        self._color = color

    def position(self):
        """ getter for position """
        return self._position

    def set_position(self, value):
        """ setter for position """
        self._position = value

    def color(self):
        """ getter for color """
        return self._color

    def set_color(self, value):
        """ setter for color """
        self._color = value

    def index(self):
        """ getter for index """
        return self._index

    def set_index(self, value):
        """ setter for index """
        self._index = value


class MarkerModel(QAbstractListModel):
    """ Model for dynamically adding multiple markers """

    IndexRole = Qt.UserRole + 1
    PositionRole = Qt.UserRole + 2
    ColorRole = Qt.UserRole + 3

    point_clicked = Signal(int, QPointF)

    _roles = {IndexRole: QByteArray(b"markerIndex"), PositionRole: QByteArray(b"markerPosition"), ColorRole: QByteArray(b"markerColor")}

    def __init__(self, parent=None):
        QAbstractListModel.__init__(self, parent)
        self._markers = []
        self._indeces = []

    @Slot(int, QPointF)
    def forward_clicked_signal(self, index: int, position: QPointF):
        self.point_clicked.emit(index, position)

    def rowCount(self, index= QModelIndex()):
        return len(self._markers)

    def roleNames(self):
        return self._roles

    def data(self, index: QModelIndex, role=Qt.DisplayRole):
        if index.row() >= self.rowCount():
            return None #QVariant()
        marker = self._markers[index.row()]

        if role == MarkerModel.IndexRole:
            return marker.index()

        if role == MarkerModel.PositionRole:
            return marker.position()

        elif role == MarkerModel.ColorRole:
            return marker.color()

        return None #QVariant()

    def setData(self, index: QModelIndex, value, role=Qt.EditRole):
        if index.isValid():
            marker = self._markers[index.row()]
            if role == MarkerModel.IndexRole:
                marker.set_index(value)

            if role == MarkerModel.PositionRole:
                marker.set_position(value)

            if role == MarkerModel.ColorRole:
                marker.set_color(value)

            self.dataChanged.emit(index, index)
            return True
        return QAbstractListModel.setData(self, index, value, role)

    def addMarker(self, position: QPointF, color= QColor("red")):
        """ adds a marker at given position with given color """
        index = QModelIndex()
        self._indeces.append(index)
        marker = MarkerItem(len(self._markers), position, color)
        self.beginInsertRows(index, self.rowCount(), self.rowCount())
        self._markers.append(marker)
        self.endInsertRows()

    def flags(self, index: QModelIndex):
        """"""
        if not index.isValid():
            return Qt.ItemIsEnabled
        return QAbstractListModel.flags(index)|Qt.ItemIsEditable
    
    def getIndexFromInt(self, i: int) -> QModelIndex:
        """  """
        return self._indeces[i]
