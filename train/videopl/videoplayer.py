"""Module contains the VideoPlayerWidget which is supposed to be a standalone window as part of the octo train app


"""

import cv2
from PySide6.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QPixmap


class VideoPlayerWidget(QWidget):
    """
    VideoPlayerWidget
    - loads a video
    - displays it with common functionality
    - emits a signal on 'export'-button press
    """
    frameExportRequest = Signal()

    def __init__(self):
        super().__init__()

        # Set up the UI
        layout = QVBoxLayout()

        self.play_button = QPushButton("Play")
        self.prev_button = QPushButton("Previous Timestamp")
        self.next_button = QPushButton("Next Timestamp")
        self.export_button = QPushButton("Export Frame")

        layout.addWidget(self.play_button)
        layout.addWidget(self.prev_button)
        layout.addWidget(self.next_button)
        layout.addWidget(self.export_button)

        self.setLayout(layout)

        # Connect button signals to their respective functions
        self.play_button.clicked.connect(self.toggle_play_pause)
        self.prev_button.clicked.connect(self.go_to_previous_timestamp)
        self.next_button.clicked.connect(self.go_to_next_timestamp)
        self.export_button.clicked.connect(self.export_frame)

        # Initialize video properties
        self.video_path = ""
        self.video_capture = None
        self.timestamps = []
        self.current_timestamp_index = 0
        self.is_playing = False

        # Timer to update the video display
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_video_frame)

    def load_video(self, video_path, timestamps):
        # Load the video and set the timestamps
        self.video_path = video_path
        self.video_capture = cv2.VideoCapture(video_path)
        self.timestamps = timestamps

        # Set the initial timestamp index and update the video display
        self.current_timestamp_index = 0
        self.update_video_frame()

    def toggle_play_pause(self):
        # Toggle play/pause state and start/stop the timer accordingly
        self.is_playing = not self.is_playing
        if self.is_playing:
            self.timer.start(33)  # 33 milliseconds (30 frames per second)
            self.prev_button.setEnabled(False)
            self.next_button.setEnabled(False)
        else:
            self.timer.stop()
            self.prev_button.setEnabled(True)
            self.next_button.setEnabled(True)

    def go_to_previous_timestamp(self):
        # Move to the previous timestamp and update the video display
        if self.current_timestamp_index > 0:
            self.current_timestamp_index -= 1
            self.update_video_frame()

    def go_to_next_timestamp(self):
        # Move to the next timestamp and update the video display
        if self.current_timestamp_index < len(self.timestamps) - 1:
            self.current_timestamp_index += 1
            self.update_video_frame()

    def update_video_frame(self):
        # Get the current timestamp and set the video capture to the corresponding frame
        current_timestamp = self.timestamps[self.current_timestamp_index]
        frame_number = int(self.video_capture.get(cv2.CAP_PROP_FPS) * current_timestamp)
        self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, frame_number)

        # Read the frame and convert it to RGB format
        ret, frame = self.video_capture.read()
        if not ret:
            self.timer.stop()
            return

        # Display the frame in the widget
        height, width, _ = frame.shape
        q_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.setFixedSize(width, height)
        self.setPixmap(q_image)

    def export_frame(self):
        # Emit the frameExportRequest signal when the 'Export' button is clicked
        self.frameExportRequest.emit()

    def setPixmap(self, q_image):
        # Update the widget with the new frame
        pixmap = QPixmap.fromImage(q_image)
        super().setPixmap(pixmap)


if __name__ == "__main__":
    app = QApplication()
    window = VideoPlayerWidget()

    # Example data (replace with your own video path and timestamps)
    video_path = ".//media//dummy.mp4"
    timestamps = [i / 30.0 for i in range(22000)]  # Assuming 30 fps (30 frames per second)

    window.load_video(video_path, timestamps)

    window.show()

    app.exec()
