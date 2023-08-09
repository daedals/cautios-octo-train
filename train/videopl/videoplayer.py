"""Module contains the VideoPlayerWidget which is supposed to be a standalone window as part of the octo train app


"""

import cv2
from numpy import ndarray
from datetime import timedelta

from PySide6.QtWidgets import QApplication, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QWidget, QLineEdit
from PySide6.QtCore import Qt, QTimer, Signal, Slot, QSize
from PySide6.QtGui import QPixmap, QImage, QResizeEvent, QIntValidator


class COTVideoPlayer(QLabel):
    """Integrates a Video loaded with OpenCV into a displayable Widget and provides functionality
    """
    video_loaded = Signal(int, str)
    frame_updated = Signal(int)

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

        # read fps information for calculation purposes
        self.video_fps = self.video_capture.get(cv2.CAP_PROP_FPS)

        # emit signal for parent, that video was loaded
        self.video_loaded.emit(timestamps[-1], video_path)

        # Set the initial timestamp index and update the video display
        self.current_timestamp_index = 0
        self._update_video_frame()

    def toggle_play_pause(self) -> bool:
        """ Toggle play/pause state and start/stop the timer accordingly """
        self.is_playing = not self.is_playing
        if self.is_playing:
            self.timer.start(1/self.video_fps)
        else:
            self.timer.stop()
        return self.is_playing

    @Slot(int)
    def jump_to_timestamp(self, sought_timestamp: int):
        """ slot for signal from parent, looks for a certain timestamp """
        if sought_timestamp >= 0 and sought_timestamp <= self.timestamps[-1]:
            # find timestamp that is closest to the sought one
            closest_timestamp = min(self.timestamps, key=lambda x:abs(x-sought_timestamp))
            self.current_timestamp_index = self.timestamps.index(closest_timestamp)
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
        """ wrapper for update video frame that advances the frame number,
            to be called by the internal timer """
        self.current_timestamp_index = (self.current_timestamp_index + 1) % len(self.timestamps)
        self._update_video_frame()

    def _update_video_frame(self):
        # Get the current timestamp and set the video capture to the corresponding frame
        # only ever frames with a gps coordinate are shown
        current_timestamp = self.timestamps[self.current_timestamp_index]
        frame_number = int(self.video_capture.get(cv2.CAP_PROP_FPS) * current_timestamp)
        self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, frame_number)

        # Read the frame and convert it to RGB format
        ret, frame = self.video_capture.read()
        if not ret:
            self.timer.stop()
            print("Something went wrong")
            return

        # Display the frame in the widget
        q_pixmap = self.convert_cv_img_to_q_pixmap(frame)
        self.setPixmap(q_pixmap)

        # signal which frame was loaded
        self.frame_updated.emit(self.current_timestamp_index)

    def convert_cv_img_to_q_pixmap(self, cv_image: ndarray):
        """Provides functionality to convert opencvs ndarray to qts pixmap """

        # fix color channels
        cv_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)

        # put the time on the image
        current_timestamp = self.timestamps[self.current_timestamp_index]
        timestamp_hhmmss = timedelta(seconds= current_timestamp)
        cv_image = cv2.putText(cv_image,
                               f"t= {timestamp_hhmmss} ({current_timestamp}s)",
                               (50,20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

        height, width, _ = cv_image.shape
        bytesPerLine = 3 * width

        unscaled_q_image = QImage(cv_image.data, width, height, bytesPerLine, QImage.Format_RGB888)
        # save unscaled image for export
        self.pixmap_unscaled = QPixmap.fromImage(unscaled_q_image)
        # unscaled_q_image = QImage(cv_image.data, width, height, bytesPerLine, QImage.Format_RGB888)
        scaled_q_image = unscaled_q_image.scaled(self.display_size.width(), self.display_size.height(), Qt.KeepAspectRatio)
        return QPixmap.fromImage(scaled_q_image)

    def resizeEvent(self, event: QResizeEvent) -> None:
        self.display_size: QSize = event.size()
        return super().resizeEvent(event)


class VideoPlayerWidget(QWidget):
    """Integrates COTVideoPlayer into a Widget and supplies UI for its functionality

    VideoPlayerWidget
    - loads a video
    - displays it with common functionality
    - emits a signal on 'export'-button press
    """
    frame_export_requested = Signal(QPixmap)

    def __init__(self):
        super().__init__()

        # Set up the UI
        general_layout = QVBoxLayout()

        self._cot_video_player = COTVideoPlayer()
        general_layout.addWidget(self._cot_video_player)

        # Create buttons
        button_widget = QWidget()
        button_layout = QHBoxLayout()

        self.play_button = QPushButton("Play")
        self.prev_button = QPushButton("Previous Timestamp")
        self.next_button = QPushButton("Next Timestamp")
        self.export_button = QPushButton("Export Frame")

        # Connect button signals to their respective functions
        self.play_button.clicked.connect(self.toggle_play_pause)
        self.prev_button.clicked.connect(self._cot_video_player.go_to_previous_timestamp)
        self.next_button.clicked.connect(self._cot_video_player.go_to_next_timestamp)
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
            lambda: self._cot_video_player.jump_to_timestamp(int(self.jump_line_edit.text()))
            )
        self._cot_video_player.video_loaded.connect(self.configure_load_dependants)

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

    # external functions
    def load_video(self, *args, **kwargs):
        """ wrapper for load_video of COTVideoPlayer """
        self._cot_video_player.load_video(*args, **kwargs)

    # external Slots
    @Slot(int)
    def set_frame_by_timestamp(self, timestamp: int) -> None:
        """ Slot for other components to request a jump """
        self._cot_video_player.jump_to_timestamp(timestamp)

    @Slot()
    def export_frame(self):
        """ Slot for export button, sends the current frames pixmap"""
        self.frame_export_requested.emit(self._cot_video_player.pixmap_unscaled)

    # internal Slots
    @Slot(int, str)
    def configure_load_dependants(self, last_timestamp: int, video_path: str):
        """ sets the text for the max jump and introduces an QIntValidator to the QLineEdit"""
        self.setWindowTitle("Video Player " + video_path)

        # configure jump widget with last possible timestamp in text and as limiter
        self.maximum_jump_tf.setText(f" < {last_timestamp}")
        self.jump_line_edit.setValidator(QIntValidator(0, last_timestamp, self))

    @Slot()
    def toggle_play_pause(self):
        """ calls COTVideoPlayers toggle and sets buttons appriopriatly """
        is_playing = self._cot_video_player.toggle_play_pause()
        if is_playing:
            self.prev_button.setEnabled(False)
            self.next_button.setEnabled(False)
            self.export_button.setEnabled(False)
        else:
            self.prev_button.setEnabled(True)
            self.next_button.setEnabled(True)
            self.export_button.setEnabled(True)
