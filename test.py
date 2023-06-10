import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QLabel, QVBoxLayout, QWidget
from PyQt6.QtGui import QImage, QPixmap, QAction
import cv2

class VideoPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Video Player")
        
        # Create actions for menu bar
        open_action = QAction("Open Video", self)
        open_action.triggered.connect(self.open_video)
        
        # Create menu bar
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")
        file_menu.addAction(open_action)
        
        # Create label widget to display video frames
        self.label = QLabel()
        
        # Create layout and add the label to it
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        
        # Create a central widget and set the layout
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        
    def open_video(self):
        file_dialog = QFileDialog()
        video_path, _ = file_dialog.getOpenFileName(self, "Open Video")
        
        if video_path:
            # Open video file
            video = cv2.VideoCapture(video_path)
            
            while video.isOpened():
                ret, frame = video.read()
                if not ret:
                    break
                
                # Convert OpenCV frame to QImage
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame_qimage = QImage(frame_rgb, frame.shape[1], frame.shape[0], QImage.Format.RGB888)
                
                # Set the QImage in the QLabel
                pixmap = QPixmap.fromImage(frame_qimage)
                self.label.setPixmap(pixmap)
                self.label.setScaledContents(True)
                
                # Display the frame
                QApplication.processEvents()
                
            video.release()

# Create the application instance
app = QApplication(sys.argv)

# Create the video player window
window = VideoPlayer()
window.show()

# Run the event loop
sys.exit(app.exec())