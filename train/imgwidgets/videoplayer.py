"""Module contains the VideoPlayerWidget which is supposed to be a standalone window as part of the octo train app


"""

import cv2
from numpy import ndarray
from datetime import timedelta

from PySide6.QtWidgets import QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QWidget, QLineEdit
from PySide6.QtCore import Qt, QTimer, Signal, Slot, QSize
from PySide6.QtGui import QPixmap, QImage, QResizeEvent, QIntValidator

from COTabc import AbstractBaseWidget
from COTdataclasses import GPSDatum, KeyFrame
from tools.handler import SessionHandler, GPSDataHandler, KeyFrameHandler

class COTVideoPlayer(QLabel):
    """ Integrates a Video loaded with OpenCV into a displayable Widget and provides functionality """

    frame_updated = Signal(GPSDatum)


    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        # Set minimum resolution to avoid scaling issues
        self.display_size = QSize(960, 540)
        self.resize(self.display_size)
        self.setMinimumSize(self.display_size)

        # Initialize video properties
        self.video_path = ""
        self.video_capture = None
        self.gpsdata: GPSDataHandler = None
        self.current_timestamp_index = 0
        self.is_playing = False

        # Timer to update the video display
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_video_frame_wrapper)

    def load_video(self, video_path: str, gpsdata: GPSDataHandler):

        # Load the video and set the timestamps from gpsdata
        self.video_path = video_path
        self.video_capture = cv2.VideoCapture(video_path)
        self.gpsdata = gpsdata

        # read fps information for calculation purposes
        self.video_fps = self.video_capture.get(cv2.CAP_PROP_FPS)
        self.image_width = cv2.CAP_PROP_FRAME_WIDTH
        self.image_height = cv2.CAP_PROP_FRAME_HEIGHT

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

    def jump_to_gpsdatum(self, gpsdatum: GPSDatum):
        """ slot for signal from parent, looks for a certain timestamp """
        self.current_timestamp_index = self.gpsdata.list_of_timestamps().index(gpsdatum.timestamp)
        self._update_video_frame()

    @Slot(int)
    def jump_to_index(self, index: int):
        """ slot for signal from parent, looks for a certain index """
        if index >= 0 and index <= len(self.gpsdata):
            self.current_timestamp_index = index
            self._update_video_frame()

    def go_to_previous_timestamp(self):
        """ Move to the previous timestamp and update the video display """
        if self.current_timestamp_index > 0:
            self.current_timestamp_index -= 1
            self._update_video_frame()

            # signal which frame was loaded
            current_gpsdatum: GPSDatum = self.gpsdata[self.current_timestamp_index]
            self.frame_updated.emit(current_gpsdatum)

    def go_to_next_timestamp(self):
        """ Move to the next timestamp and update the video display """
        if self.current_timestamp_index < len(self.gpsdata) - 1:
            self.current_timestamp_index += 1
            self._update_video_frame()

            # signal which frame was loaded
            current_gpsdatum: GPSDatum = self.gpsdata[self.current_timestamp_index]
            self.frame_updated.emit(current_gpsdatum)

    def _update_video_frame_wrapper(self):
        """ wrapper for update video frame that advances the frame number,
            to be called by the internal timer """
        self.current_timestamp_index = (self.current_timestamp_index + 1) % len(self.gpsdata)
        self._update_video_frame()
        
        # signal which frame was loaded
        current_gpsdatum: GPSDatum = self.gpsdata[self.current_timestamp_index]
        self.frame_updated.emit(current_gpsdatum)

    def _update_video_frame(self):
        # Get the current timestamp and set the video capture to the corresponding frame
        # only ever frames with a gps coordinate are shown
        current_gpsdatum: GPSDatum = self.gpsdata[self.current_timestamp_index]
        frame_number = int(self.video_capture.get(cv2.CAP_PROP_FPS) * current_gpsdatum.timestamp)
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

    def convert_cv_img_to_q_pixmap(self, cv_image: ndarray):
        """Provides functionality to convert opencvs ndarray to qts pixmap """

        # fix color channels
        cv_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)

        # put the time on the image
        current_gpsdatum: GPSDatum = self.gpsdata[self.current_timestamp_index]
        timestamp_hhmmss = timedelta(seconds= current_gpsdatum.timestamp)
        cv_image = cv2.putText(cv_image,
                               f"t= {timestamp_hhmmss} ({current_gpsdatum.timestamp}s)",
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


class VideoPlayerWidget(AbstractBaseWidget):
    """Integrates COTVideoPlayer into a Widget and supplies UI for its functionality

    VideoPlayerWidget
    - loads a video
    - displays it with common functionality
    """

    ################################## Implementation of abstract methods ###########################################

    def _initialize(self):
        # Set up the VIdeoplayer
        self._cot_video_player = COTVideoPlayer()
        self._cot_video_player.load_video(
            self._session_handler.session_data.video_file_path,
            self._gpsdata_handler
        )

        self._session_handler.session_data.image_width = self._cot_video_player.image_width
        self._session_handler.session_data.image_height = self._cot_video_player.image_height

        # connect wrapper for signal
        self._cot_video_player.frame_updated.connect(self.frame_updated_wrapper)

    def _setup_ui(self):
        # Set general Info
        self._widget.setWindowTitle("Video Player " + self._session_handler.session_data.video_file_path.split("/")[-1])

        # Create general layout
        general_layout = QVBoxLayout()
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

        # Create widget with jump to index functionality
        jump_widget = QWidget()
        jump_layout = QHBoxLayout()

        # Create sub widgets
        last_timestamp = self._gpsdata_handler[-1].timestamp

        textfield1 = QLabel("Jump to:")
        minimum_jump_tf = QLabel("0 ≤ ")
        self.jump_line_edit = QLineEdit("0")
        maximum_jump_tf = QLabel(str(last_timestamp))
        jump_button = QPushButton("Jump")

        self.jump_line_edit.setValidator(QIntValidator(0, last_timestamp, self._widget))

        # connect to signals
        jump_button.clicked.connect(
            lambda: self._gpsdata_handler.request_gpsdatum(
                self._gpsdata_handler.closest_datum_by_timestamp(int(self.jump_line_edit.text()))
                )
            )

        # add to layout
        jump_layout.addWidget(textfield1)
        jump_layout.addWidget(minimum_jump_tf)
        jump_layout.addWidget(self.jump_line_edit)
        jump_layout.addWidget(maximum_jump_tf)
        jump_layout.addWidget(jump_button)

        jump_widget.setLayout(jump_layout)

        # add button widget to UI
        general_layout.addWidget(button_widget)
        general_layout.addWidget(jump_widget)
        self._widget.setLayout(general_layout)
        

        # configure jump widget with last possible timestamp in text and as limiter

    def react_to_keyframe_change(self, keyframe: KeyFrame):
        self.react_to_gpsdatum_change(keyframe.gps)

    def react_to_gpsdatum_change(self, gpsdatum: GPSDatum):
        self.jump_line_edit.setText(str(gpsdatum.timestamp))
        self._cot_video_player.jump_to_gpsdatum(gpsdatum)

    ################################## Implementation of class methods ###########################################

    @Slot()
    def export_frame(self):
        """ Slot for export button, sends the current frames pixmap"""
        keyframe = KeyFrame(
            self._gpsdata_handler[self._cot_video_player.current_timestamp_index],
            self._cot_video_player.pixmap_unscaled,
            None, None, None
        )

        self._keyframe_handler.request_keyframe(keyframe)

    # internal Slots
    @Slot(int)
    def frame_updated_wrapper(self, gpsdatum: GPSDatum):
        """ wraps COT_Video_Players signal for other components to access """
        self._gpsdata_handler.request_gpsdatum(gpsdatum)

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
