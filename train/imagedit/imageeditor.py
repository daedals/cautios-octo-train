import sys
from PySide6.QtCore import Signal, QLineF, QRectF
from PySide6.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget, QGraphicsView, QGraphicsScene, QHBoxLayout
from PySide6.QtGui import QPixmap, QPainter, QPen, QColor, QMouseEvent

class InteractableGraphicsView(QGraphicsView):
    """Renders choosen key frame and handles mouse events for an interactable image

    Renders exactly 4 points and lines connecting them
    """
    pointsChanged = Signal(int, int, int)

    def __init__(self, _pixmap: QPixmap, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # prepare graphics scene
        self._original_image: QPixmap = _pixmap
        self.scene = QGraphicsScene(0, 0, self._original_image.width(), self._original_image.height())
        self.setScene(self.scene)
        self.scene.addPixmap(self._original_image)
        self.setSceneRect(0, 0, self._original_image.width(), self._original_image.height())
        # self.ensureVisible(0, 0, self._original_image.width(), self._original_image.height())

        # prepare internal point storage
        self.points = []
        self.current_point_index = 0


    def draw_points(self):
        """clear graphicsscene and draw points and lines from buffer
        """
        # prepare scene and pen
        self.scene.clear()
        self.scene.addPixmap(self._original_image)
        pen = QPen(QColor(255, 0, 0))

        # draw lines between
        if len(self.points) > 1:
            for i, (x1, y1) in enumerate(self.points):
                # dont draw final line if not 4 points are set
                if i+1 == len(self.points) and not (i+1)%4 == 0:
                    break

                # get following point and draw line
                x2, y2 = self.points[(i+1)%len(self.points)]
                line = QLineF(x1, y1, x2, y2)
                self.scene.addLine(line, pen)

        # Draw circles at each point
        for i, (x, y) in enumerate(self.points):
            ellipse = QRectF(x - 3, y - 3, 6, 6)
            self.scene.addEllipse(ellipse, pen)

        # Update the scene with the updated image

    def mousePressEvent(self, event: QMouseEvent):
        """Function to handle mouse click events on the image
        """
        
        # Get the mouse coordinates and add the point to the list
        x = int(event.position().x())
        y = int(event.position().y())

        x = int(self.mapToScene(x,y).x())
        y = int(self.mapToScene(x,y).y())

        # print(f"IGV:" +
        #       f"\n{event.position()}\n" +
        #       f"{event.scenePosition()}\n" +
        #       f"{self.mapFromScene(event.scenePosition())}\n" +
        #       f"{self.mapToScene(int(event.scenePosition().x()), int(event.scenePosition().y()))}\n" +
        #       f"{self.mapToScene(x, y)}\n"
        #       )

        if len(self.points) > self.current_point_index:
            self.points[self.current_point_index] = (x, y)
        else:
            self.points.append((x, y))

        # # Update the corresponding button label with the image coordinates
        # self.buttons[self.current_point_index].setText(f"Point {self.current_point_index + 1} ({x}, {y})")

        self.draw_points()

        # Move to the next point index
        self.current_point_index = (self.current_point_index + 1)%4






class ImageViewerWidget(QWidget):
    """Standalone Window providing utility for InteractableGraphicsView
    """
    def __init__(self, pixmap: QPixmap):
        super().__init__()

        # Set up the UI
        layout = QVBoxLayout()

        # Create a QGraphicsView to allow interactive drawing
        self.view = InteractableGraphicsView(pixmap)
        layout.addWidget(self.view)

        # Create buttons for points and connect them to the point_clicked function
        self.buttons = []
        button_row = QWidget()
        button_row_layout = QHBoxLayout()

        for i in range(1, 5):
            button = QPushButton(f"Point {i}")
            button.clicked.connect(lambda checked=False, point=i: self.point_clicked(checked, point))
            self.buttons.append(button)
            button_row_layout.addWidget(button)
        button_row.setLayout(button_row_layout)

        layout.addWidget(button_row)

        # Create an "Export" button and connect it to the export_button_clicked function
        self.export_button = QPushButton("Export")
        self.export_button.clicked.connect(self.export_button_clicked)
        layout.addWidget(self.export_button)

        # Initialize point list and current point index
        self.points = []
        self.current_point_index = 0

        # Set the main layout
        self.setLayout(layout)

        # Draw the points on the image
        self.view.draw_points()

    def point_clicked(self, checked, point):
        # Function to handle point button clicks
        print(checked, point)
        self.current_point_index = point - 1
        self.view.draw_points()

    def export_button_clicked(self):
        # Emit the "exportImagePointRequest" signal with the current points list
        self.exportImagePointRequest.emit(self.points)

    def mousePressEvent(self, event: QMouseEvent):
        """Function to handle mouse click events on the image
        """
        
        # Get the mouse coordinates and add the point to the list
        x = int(event.position().x())
        y = int(event.position().y())

        print(f"IVW:\n{event.position().x()}, {event.position().y()}\n{event.localPos().x()}, {event.localPos().y()}\n{event.scenePosition().x()}, {event.scenePosition().y()}\n")

        if len(self.points) > self.current_point_index:
            self.points[self.current_point_index] = (x, y)
        else:
            self.points.append((x, y))

        # Update the corresponding button label with the image coordinates
        self.buttons[self.current_point_index].setText(f"Point {self.current_point_index + 1} ({x}, {y})")

        self.view.draw_points()

        # Move to the next point index
        self.current_point_index = (self.current_point_index + 1)%4


if __name__ == "__main__":
    app = QApplication(sys.argv)
    pixmap = QPixmap(".//media//dummy.jpg")
    window = ImageViewerWidget(pixmap)
    window.show()

    sys.exit(app.exec())