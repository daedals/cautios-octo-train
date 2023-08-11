""" Contains class definitions for InteractableGraphicsView and ImageViewerWidget """

import sys
from PySide6.QtCore import Signal, Slot, QLineF, QRectF
from PySide6.QtWidgets import QPushButton, QVBoxLayout, QWidget, \
                              QGraphicsView, QGraphicsScene, QHBoxLayout
from PySide6.QtGui import QPixmap, QPen, QColor, QMouseEvent

from COTdataclasses import KeyFrame, GPSDatum, ImagePointContainer
from COTabc import AbstractBaseWidget
from tools.math import assign_points_to_assumed_order

class InteractableGraphicsView(QGraphicsView):
    """ Renders choosen key frame and handles mouse events for an interactable image

    Renders exactly 4 points and lines connecting them
    """
    point_changed = Signal(int, int, int)

    def __init__(self, width: int, height: int, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # prepare graphics scene
        self.scene = QGraphicsScene(0, 0, width, height, self)
        self.setScene(self.scene)
        # self.setSceneRect(0, 0, width, height)

    def load_keyframe(self, keyframe: KeyFrame) -> None:
        # is called when keyframe was created or loaded
        self._original_image: QPixmap = keyframe.pixmap

        self.points = []
        if keyframe.image_point is not None:
            for i, [x, y] in enumerate(keyframe.image_point.to_list()):
                self.points.append([x, y])
                self.point_changed.emit(i, x, y)

        self.current_point_index = 0
        self.draw_points()

    def draw_points(self):
        """ clear graphicsscene and draw points and lines from buffer """
        # prepare scene and pen
        self.scene.clear()
        self.scene.addPixmap(self._original_image)
        self.setSceneRect(0, 0, self._original_image.width(), self._original_image.height())
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
            self.points[self.current_point_index] = [x, y]
        else:
            self.points.append([x, y])

        # Draw points
        self.draw_points()

        # Emit Signal that point changed
        self.point_changed.emit(self.current_point_index, x, y)

        # Move to the next point index
        if len(self.points) < 4:
            self.current_point_index = (self.current_point_index + 1)%4


class ImageViewerWidget(AbstractBaseWidget):
    """ Standalone Window providing utility for InteractableGraphicsView """

    ################################## Implementation of abstract methods ###########################################

    def _initialize(self):
        pass

    def _setup_ui(self):
        # Set up the UI
        layout = QVBoxLayout()

        # Create a QGraphicsView to allow interactive drawing
        self.view = InteractableGraphicsView(
            self._session_handler.session_data.image_width,
            self._session_handler.session_data.image_height
        )

        self.view.point_changed.connect(self.on_points_changed)
        layout.addWidget(self.view)

        # Create buttons for points and connect them to the point_clicked function
        self.buttons = []
        button_row = QWidget()
        button_row_layout = QHBoxLayout()

        # Connect 4 buttons to a point each
        for i in range(1, 5):
            button = QPushButton(f"Point {i}")
            button.clicked.connect(lambda checked=False, point=i: self.point_button_clicked(checked, point))
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
        self._widget.setLayout(layout)

    def react_to_keyframe_change(self, keyframe: KeyFrame):
        # reset buttons
        for i in range(1, 5):
            self.buttons[i-1].setText(f"Point {i}")
        # remember current keyframe for exporting them later
        self.current_keyframe = keyframe
        self.view.load_keyframe(keyframe)
        self.show()

    def react_to_gpsdatum_change(self, gpsdatum: GPSDatum):
        pass


    ################################## Implementation of class methods ###########################################

    def point_button_clicked(self, _, point: int):
        """ Function to handle point button clicks """
        self.view.set_current_index(point - 1)

    def export_button_clicked(self):
        """ Emit the "exportImagePointRequest" signal with the current points list """
        image_points = self.view.points
        a, b, c, d = assign_points_to_assumed_order(image_points)
        ipc = ImagePointContainer(a, b, c, d)
        self.current_keyframe.image_point = ipc
        self._keyframe_handler.request_keyframe(self.current_keyframe)

    @Slot(int, int, int)
    def on_points_changed(self, i, x, y):
        """ Function to handle mouse click events on the image """
        self.buttons[i].setText(f"Point {i+1} ({x}, {y})")
        if not self.export_button_enabled and len(self.view.points) == 4:
            self.export_button_enabled = True
            self.export_button.setDisabled(False)
