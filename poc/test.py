import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QLabel, QVBoxLayout, QWidget, QPushButton
from PyQt6.QtGui import QImage, QPixmap, QAction
from PyQt6.QtCore import QThread, Qt, pyqtSignal
import cv2


class VideoPlayerThread(QThread):
    frame_changed = pyqtSignal(QImage)

    def __init__(self):
        super().__init__()
        self.video_paused = True
        self.video_path = ""
        self.video = None

    def load_video(self, video_path):
        self.video_path = video_path

    def play_video(self):
        self.video_paused = False

    def pause_video(self):
        self.video_paused = True

    def reset_video(self):
        self.pause_video()
        if self.video is not None:
            self.video.set(cv2.CAP_PROP_POS_FRAMES, 0)
            self.update_frame()

    def step_forward(self):
        if not self.video_paused:
            return

        if self.video is not None:
            current_frame = self.video.get(cv2.CAP_PROP_POS_FRAMES)
            total_frames = self.video.get(cv2.CAP_PROP_FRAME_COUNT)
            new_frame = int(current_frame)

            if new_frame >= total_frames:
                new_frame = total_frames - 2

            self.video.set(cv2.CAP_PROP_POS_FRAMES, new_frame)
            self.update_frame()

    def step_backward(self):
        if not self.video_paused:
            return

        if self.video is not None:
            current_frame = self.video.get(cv2.CAP_PROP_POS_FRAMES)
            total_frames = self.video.get(cv2.CAP_PROP_FRAME_COUNT)
            new_frame = int(current_frame) - 2

            if new_frame < 0:
                new_frame = 0

            self.video.set(cv2.CAP_PROP_POS_FRAMES, new_frame)
            self.update_frame()

    def run(self):
        if self.video_path:
            self.video = cv2.VideoCapture(self.video_path)
            while True:
                if not self.video_paused:
                    ret, frame = self.video.read()
                    if not ret:
                        break

                    # Convert OpenCV frame to QImage
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frame_qimage = QImage(frame_rgb, frame.shape[1], frame.shape[0], QImage.Format.Format_RGB888)

                    self.frame_changed.emit(frame_qimage)

                self.msleep(30)  # 30ms delay

    def update_frame(self):
        if self.video is not None:
            ret, frame = self.video.read()
            if ret:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame_qimage = QImage(frame_rgb, frame.shape[1], frame.shape[0], QImage.Format.Format_RGB888)
                self.frame_changed.emit(frame_qimage)


class VideoPlayerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Video Player")

        self.video_player = VideoPlayerThread()
        self.video_player.frame_changed.connect(self.update_frame)

        # Create actions for menu bar
        open_action = QAction("Open Video", self)
        open_action.triggered.connect(self.open_video)

        # Create menu bar
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")
        file_menu.addAction(open_action)

        # Create label widget to display video frames
        self.label = QLabel()

        # Create buttons for control
        self.play_button = QPushButton("Play")
        self.play_button.clicked.connect(self.play_pause_video)

        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self.reset_video)

        self.step_forward_button = QPushButton("Step Forward")
        self.step_forward_button.clicked.connect(self.step_forward)

        self.step_backward_button = QPushButton("Step Backward")
        self.step_backward_button.clicked.connect(self.step_backward)

        # Disable control buttons initially
        self.play_button.setEnabled(False)
        self.reset_button.setEnabled(False)
        self.step_forward_button.setEnabled(False)
        self.step_backward_button.setEnabled(False)

        # Create layout and add widgets to it
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.play_button)
        layout.addWidget(self.reset_button)
        layout.addWidget(self.step_forward_button)
        layout.addWidget(self.step_backward_button)

        # Create a central widget and set the layout
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def open_video(self):
        file_dialog = QFileDialog()
        video_path, _ = file_dialog.getOpenFileName(self, "Open Video")

        if video_path:
            self.video_player.load_video(video_path)
            self.video_player.start()
            self.play_button.setEnabled(True)
            self.reset_button.setEnabled(True)
            self.step_forward_button.setEnabled(True)
            self.step_backward_button.setEnabled(True)
            self.video_player.reset_video()

    def play_pause_video(self):
        if self.video_player.video_paused:
            self.video_player.play_video()
            self.play_button.setText("Pause")
        else:
            self.video_player.pause_video()
            self.play_button.setText("Play")

    def reset_video(self):
        if not self.video_player.video_paused:
            self.play_button.setText("Play")
        self.video_player.reset_video()

    def step_forward(self):
        self.video_player.step_forward()

    def step_backward(self):
        self.video_player.step_backward()

    def update_frame(self, frame):
        pixmap = QPixmap.fromImage(frame)
        self.label.setPixmap(pixmap)


# Create the application instance
app = QApplication(sys.argv)

# Create the video player window
window = VideoPlayerWindow()
window.show()

# Run the event loop
sys.exit(app.exec())