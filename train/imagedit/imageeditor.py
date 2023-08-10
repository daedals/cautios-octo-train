"""Contains class definitions for InteractableGraphicsView and ImageViewerWidget
"""

import sys
from PySide6.QtCore import Signal, Slot, QLineF, QRectF
from PySide6.QtWidgets import QPushButton, QVBoxLayout, QWidget, \
                              QGraphicsView, QGraphicsScene, QHBoxLayout
from PySide6.QtGui import QPixmap, QPen, QColor, QMouseEvent

from COTdataclasses import KeyFrame

class InteractableGraphicsView(QGraphicsView):
    """ Renders choosen key frame and handles mouse events for an interactable image

    Renders exactly 4 points and lines connecting them
    """
    pointsChanged = Signal(int, int, int)

    def __init__(self, _pixmap: QPixmap, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # prepare graphics scene
        self._original_image: QPixmap = _pixmap
        self.scene = QGraphicsScene(
            0, 0,
            self._original_image.width(), self._original_image.height()
            )
        self.setScene(self.scene)
        self.scene.addPixmap(self._original_image)
        self.setSceneRect(0, 0, self._original_image.width(), self._original_image.height())
        # self.ensureVisible(0, 0, self._original_image.width(), self._original_image.height())

        # prepare internal point storage
        self.points = []
        self.current_point_index = 0

    def draw_points(self):
        """ clear graphicsscene and draw points and lines from buffer """
        # prepare scene and pen
        self.scene.clear()
        self.scene.addPixmap(self._original_image)
        pen = QPen(QColor(255, 0, 0))

        # draw lines between
        if len(self.points) > 1:
            for i, (x_1, y_1) in enumerate(self.points):
                # dont draw final line if not 4 points are set
                if i+1 == len(self.points) and not (i+1)%4 == 0:
                    break

                # get following point and draw line
                x_2, y_2 = self.points[(i+1)%len(self.points)]
                line = QLineF(x_1, y_1, x_2, y_2)
                self.scene.addLine(line, pen)

        # Draw circles at each point
        for i, (x, y) in enumerate(self.points):
            ellipse = QRectF(x - 3, y - 3, 6, 6)
            self.scene.addEllipse(ellipse, pen)

        # Update the scene with the updated image

    def set_current_index(self, desired_index: int):
        """ Set current index as requested if there are points before that index """
        self.current_point_index = desired_index \
            if len(self.points) >= desired_index \
            else len(self.points)

    def mousePressEvent(self, event: QMouseEvent):
        """ Function to handle mouse click events on the image """

        # Get the mouse coordinates translate them to the picture
        x = int(event.position().x())
        y = int(event.position().y())

        x = int(self.mapToScene(x,y).x())
        y = int(self.mapToScene(x,y).y())

        # Add points
        if len(self.points) > self.current_point_index:
            self.points[self.current_point_index] = (x, y)
        else:
            self.points.append((x, y))

        # Draw points
        self.draw_points()

        # Emit Signal that point changed
        self.pointsChanged.emit(self.current_point_index, x, y)

        # Move to the next point index
        if len(self.points) < 4:
            self.current_point_index = (self.current_point_index + 1)%4


class ImageViewerWidget(QWidget):
    """ Standalone Window providing utility for InteractableGraphicsView """

    export_image_points_requested = Signal(list)

    def __init__(self, _keyframe: KeyFrame):
        super().__init__()

        # Set up the UI
        layout = QVBoxLayout()

        self._keyframe = _keyframe

        # Create a QGraphicsView to allow interactive drawing
        self.view = InteractableGraphicsView(_keyframe.pixmap)
        self.view.pointsChanged.connect(self.on_points_changed)
        layout.addWidget(self.view)

        # Create buttons for points and connect them to the point_clicked function
        self.buttons = []
        button_row = QWidget()
        button_row_layout = QHBoxLayout()

        # Connect 4 buttons to a point each
        for i in range(1, 5):
            button = QPushButton(f"Point {i}")
            button.clicked.connect(lambda checked=False, point=i: self.point_clicked(checked, point))
            self.buttons.append(button)
            button_row_layout.addWidget(button)
        button_row.setLayout(button_row_layout)

        layout.addWidget(button_row)

        # Create an "Export" button and connect it to the export_button_clicked function, disable it
        self.export_button = QPushButton("Export")
        self.export_button.clicked.connect(self.export_button_clicked)
        self.export_button.setDisabled(True)
        self.export_button_enabled = False
        layout.addWidget(self.export_button)

        # Set the main layout
        self.setLayout(layout)

    def point_clicked(self, _, point):
        """ Function to handle point button clicks """
        self.view.set_current_index(point -1)

    def export_button_clicked(self):
        """ Emit the "exportImagePointRequest" signal with the current points list """
        self.export_image_points_requested.emit(self.view.points)

    @Slot(int, int, int)
    def on_points_changed(self, i, x, y):
        """ Function to handle mouse click events on the image """
        self.buttons[i].setText(f"Point {i+1} ({x}, {y})")
        if not self.export_button_enabled and len(self.view.points) == 4:
            self.export_button_enabled = True
            self.export_button.setDisabled(False)
