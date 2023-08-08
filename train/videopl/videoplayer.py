"""Module contains the VideoPlayerWidget which is supposed to be a standalone window as part of the octo train app


"""

import cv2
from numpy import ndarray
from PySide6.QtWidgets import QApplication, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QWidget, QLineEdit
from PySide6.QtCore import Qt, QTimer, Signal, Slot, QSize
from PySide6.QtGui import QPixmap, QImage, QResizeEvent, QIntValidator


class VideoPlayerLabel(QLabel):
    """Integrates a Video loaded with OpenCV into a displayable Widget and provides functionality
    """
    video_loaded = Signal(int)

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        # Set minimum resolution to avoid scaling issues
        self.display_size = QSize(960, 540)
        self.resize(self.display_size)
        self.setMinimumSize(self.display_size)

        # Initialize video properties
        self.video_path = ""
        self.video_capture = None
        self.timestamps = []
        self.current_timestamp_index = 0
        self.is_playing = False

        # Timer to update the video display
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_video_frame_wrapper)

    def load_video(self, video_path: str, timestamps: list = [0]):

        # Load the video and set the timestamps
        self.video_path = video_path
        self.video_capture = cv2.VideoCapture(video_path)
        self.timestamps = timestamps

        self.video_loaded.emit(len(timestamps))

        self.video_fps = self.video_capture.get(cv2.CAP_PROP_FPS)

        # Set the initial timestamp index and update the video display
        self.current_timestamp_index = 0
        self._update_video_frame()
        
    def toggle_play_pause(self) -> bool:
        """Toggle play/pause state and start/stop the timer accordingly
        """
        self.is_playing = not self.is_playing
        if self.is_playing:
            self.timer.start(1/self.video_fps)  # 33 milliseconds (30 frames per second)
        else:
            self.timer.stop()
        return self.is_playing
    def jump_to_index(self, index: int):
        if index >= 0 and index < len(self.timestamps):
            self.current_timestamp_index = index
            self._update_video_frame()

    def go_to_previous_timestamp(self):
        # Move to the previous timestamp and update the video display
        if self.current_timestamp_index > 0:
            self.current_timestamp_index -= 1
            self._update_video_frame()

    def go_to_next_timestamp(self):
        # Move to the next timestamp and update the video display
        if self.current_timestamp_index < len(self.timestamps) - 1:
            self.current_timestamp_index += 1
            self._update_video_frame()

    def _update_video_frame_wrapper(self):
        """wrapper for update video frame that advances the frame number, to be called by the internal timer
        """
        self.current_timestamp_index = (self.current_timestamp_index + 1) % len(self.timestamps)
        self._update_video_frame()

    def _update_video_frame(self):
        # Get the current timestamp and set the video capture to the corresponding frame
        current_timestamp = self.timestamps[self.current_timestamp_index]
        frame_number = int(self.video_capture.get(cv2.CAP_PROP_FPS) * current_timestamp)
        self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, frame_number)

        # Read the frame and convert it to RGB format
        ret, frame = self.video_capture.read()
        if not ret:
            self.timer.stop()
            print("SOmething went wrong")
            return

        # Display the frame in the widget
        q_image = self.convert_cv_img_to_q_pixmap(frame)
        self.setPixmap(q_image)

    def convert_cv_img_to_q_pixmap(self, cv_image: ndarray):
        """Provides functionality to convert opencvs ndarray to qts pixmap """
        height, width, _ = cv_image.shape
        bytesPerLine = 3 * width

        unscaled_q_image = QImage(cv_image.data, width, height, bytesPerLine, QImage.Format_RGB888)
        # unscaled_q_image = QImage(cv_image.data, width, height, bytesPerLine, QImage.Format_RGB888)
        scaled_q_image = unscaled_q_image.scaled(self.display_size.width(), self.display_size.height(), Qt.KeepAspectRatio)
        return QPixmap.fromImage(scaled_q_image)

    def resizeEvent(self, event: QResizeEvent) -> None:
        self.display_size: QSize = event.size()
        return super().resizeEvent(event)


class VideoPlayerWidget(QWidget):
    """Integrates VideoplayerLabel into a Widget and supplies UI for its functionality

    VideoPlayerWidget
    - loads a video
    - displays it with common functionality
    - emits a signal on 'export'-button press
    """
    frameExportRequest = Signal(QPixmap)

    def __init__(self):
        super().__init__()

        # Set up the UI
        general_layout = QVBoxLayout()

        self.video_player_label = VideoPlayerLabel()
        general_layout.addWidget(self.video_player_label)

        # Create buttons
        button_widget = QWidget()
        button_layout = QHBoxLayout()

        self.play_button = QPushButton("Play")
        self.prev_button = QPushButton("Previous Timestamp")
        self.next_button = QPushButton("Next Timestamp")
        self.export_button = QPushButton("Export Frame")

        # Connect button signals to their respective functions
        self.play_button.clicked.connect(self.toggle_play_pause)
        self.prev_button.clicked.connect(self.video_player_label.go_to_previous_timestamp)
        self.next_button.clicked.connect(self.video_player_label.go_to_next_timestamp)
        self.export_button.clicked.connect(self.export_frame)

        # Add buttons to UI
        button_layout.addWidget(self.play_button)
        button_layout.addWidget(self.prev_button)
        button_layout.addWidget(self.next_button)
        button_layout.addWidget(self.export_button)

        button_widget.setLayout(button_layout)

        # create widget with jump to index functionality
        jump_widget = QWidget()
        jump_layout = QHBoxLayout()

        # create sub widgets
        textfield1 = QLabel("Jump to:")
        minimum_jump_tf = QLabel("0 ≤ ")
        self.jump_line_edit = QLineEdit("0")
        self.maximum_jump_tf = QLabel("")
        self.jump_button = QPushButton("Jump")

        # connect to signals
        self.jump_button.clicked.connect(
            lambda: self.video_player_label.jump_to_index(int(self.jump_line_edit.text()))
            )
        self.video_player_label.video_loaded.connect(self.configure_jump_widget)

        # add to layout
        jump_layout.addWidget(textfield1)
        jump_layout.addWidget(minimum_jump_tf)
        jump_layout.addWidget(self.jump_line_edit)
        jump_layout.addWidget(self.maximum_jump_tf)
        jump_layout.addWidget(self.jump_button)

        jump_widget.setLayout(jump_layout)

        # add button widget to UI
        general_layout.addWidget(button_widget)
        general_layout.addWidget(jump_widget)
        self.setLayout(general_layout)

    def load_video(self, *args, **kwargs):
        """ wrapper for load_video of videoplayerlabel """
        self.video_player_label.load_video(*args, **kwargs)

    @Slot(int)
    def configure_jump_widget(self, max_index: int):
        """ sets the text for the max jump and introduces an QIntValidator to the QLineEdit"""
        self.maximum_jump_tf.setText(f" < {max_index}")
        self.jump_line_edit.setValidator(QIntValidator(0, max_index-1, self))

    def export_frame(self):
        """ Slot for export button, sends the current frames pixmap"""
        self.frameExportRequest.emit(self.video_player_label.pixmap)

    def toggle_play_pause(self):
        is_playing = self.video_player_label.toggle_play_pause()
        if is_playing:
            self.prev_button.setEnabled(False)
            self.next_button.setEnabled(False)
            self.export_button.setEnabled(False)
        else:
            self.prev_button.setEnabled(True)
            self.next_button.setEnabled(True)
            self.export_button.setEnabled(True)

    # def resizeEvent(self, event: QResizeEvent) -> None:
    #     # self.video_player_label.adjustSize()
    #     return super().resizeEvent(event)



if __name__ == "__main__":
    app = QApplication()
    window = VideoPlayerWidget()

    # video_path = "D:\\nordlandsbanen.spring.sync.1920x1080.h264.nrk.mp4"
    video_path = "D:\\nordlandsbanen.winter.sync.1920x1080.h264.nrk.mp4"
    window.video_player_label.load_video(video_path, [i for i in range(0, 2000)])

    window.show()
    app.exec()
