from PyQt6.QtGui import QPixmap, QPainter, QPen
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel
import sys


class ClickableImage(QPixmap):
    def __init__(self, width, height):
        super().__init__(width, height)
        self.fill(Qt.GlobalColor.white)
        self.points = []

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and len(self.points) < 4:
            # Convert mouse coordinates to image coordinates
            image_pos = QPoint(event.pos().x(), event.pos().y())

            # Store the clicked point
            self.points.append(image_pos)

            # Redraw the image to display the points
            self.drawPoints()

    def drawPoints(self):
        self.fill(Qt.GlobalColor.white)

        painter = QPainter(self)
        painter.setPen(QPen(Qt.GlobalColor.red, 5))

        for point in self.points:
            painter.drawPoint(point)

        painter.end()


# Create the application instance
app = QApplication(sys.argv)

# Create the clickable image
image = ClickableImage(800, 600)

label = QLabel()
label.setPixmap(image)

# Create a main window to display the image
main_window = QMainWindow()
main_window.setCentralWidget(label)
main_window.setWindowTitle("Clickable Image")
main_window.setGeometry(100, 100, 800, 600)
main_window.show()

# Run the event loop
sys.exit(app.exec())