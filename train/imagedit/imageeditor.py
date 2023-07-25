import sys
from PySide6.QtWidgets import QApplication, QLabel, QPushButton, QVBoxLayout, QWidget, QGraphicsView, QGraphicsScene
from PySide6.QtGui import QPixmap, QPainter, QPen, QColor


class ImageViewerWidget(QWidget):
    def __init__(self, image_path):
        super().__init__()

        # Set up the UI
        layout = QVBoxLayout()

        # Load the image and display it in the widget
        self.image_label = QLabel()
        self.load_image(image_path)

        # Create a QGraphicsScene and QGraphicsView to allow interactive drawing
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setSceneRect(0, 0, self.image.width(), self.image.height())
        layout.addWidget(self.view)

        # Create buttons for points and connect them to the point_clicked function
        self.buttons = []
        for i in range(1, 5):
            button = QPushButton(f"Point {i}")
            button.clicked.connect(lambda checked, point=i: self.point_clicked(checked, point))
            self.buttons.append(button)
            layout.addWidget(button)

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
        self.draw_points()

    def load_image(self, image_path):
        # Load the image from the given file path and display it
        self.image = QPixmap(image_path)
        self.image_label.setPixmap(self.image)

    def point_clicked(self, checked, point):
        # Function to handle point button clicks
        print(checked, point)
        self.current_point_index = point - 1
        self.draw_points()

    def draw_points(self):
        # Function to draw points and lines on the image
        painter = QPainter(self.image)
        pen = QPen(QColor(255, 0, 0))  # Red pen for drawing points and lines

        if len(self.points) > 2:
            for i in range(len(self.points)):
                painter.setPen(pen)
                x1, y1 = self.points[i]
                x2, y2 = self.points[(i+1)%len(self.points)]
                painter.drawLine(x1, y1, x2, y2)

        # Draw circles at each point
        for i, (x, y) in enumerate(self.points):
            painter.setPen(pen)
            painter.drawEllipse(x - 3, y - 3, 6, 6)
            # Update the corresponding button label with the image coordinates
            self.buttons[i].setText(f"Point {i + 1} ({x}, {y})")

        painter.end()

        # Update the image label with the updated image
        self.image_label.setPixmap(self.image)

    def export_button_clicked(self):
        # Emit the "exportImagePointRequest" signal with the current points list
        self.exportImagePointRequest.emit(self.points)

    def mousePressEvent(self, event):
        # Function to handle mouse click events on the image
        
        # Get the mouse coordinates and add the point to the list
        x = int(event.position().x())
        y = int(event.position().y())

        if len(self.points) > self.current_point_index:
            self.points[self.current_point_index] = (x, y)
        else:
            self.points.append((x, y))

        self.draw_points()

        # Move to the next point index
        self.current_point_index = (self.current_point_index + 1)%4


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageViewerWidget(".//media//dummy.jpg")
    window.show()

    sys.exit(app.exec())
