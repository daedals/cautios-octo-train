""" file picker """

import os

from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import QVBoxLayout, QWidget, QFileDialog,\
                              QLabel, QPushButton, QMenuBar
from PySide6.QtGui import QAction

from tools.handler import SessionHandler

class FilePickerWidget(QWidget):
    """
    basic application for opening a file dialog/ restoring a session by choosing the respective option in the menubar
    """
    import_requested = Signal()

    valid_video_file_extensions = [".mp4", ".avi", ".mov"]
    valid_gpsdata_file_extensions = [".csv"]


    def __init__(self, session: SessionHandler, menubar: QMenuBar):
        super().__init__()

        self.session = session

        # Create the layout
        self.setMinimumWidth(400)
        main_layout = QVBoxLayout()

        # Create the text boxes and a button
        self.video_path_textbox = QLabel(
            f"No path to video specified ({FilePickerWidget.valid_video_file_extensions})"
            )
        self.gps_data_path_textbox = QLabel(
            f"No path to gps data specified ({FilePickerWidget.valid_gpsdata_file_extensions})"
            )
        self.import_button = QPushButton(text= "Import")

        # Prepare Button
        self.import_button.clicked.connect(self.import_button_clicked)

        # Add the text boxes to the layout
        main_layout.addWidget(self.video_path_textbox)
        main_layout.addWidget(self.gps_data_path_textbox)
        main_layout.addWidget(self.import_button)

        self.setLayout(main_layout)

        # Create "Open Video" action and connect it to the slot
        open_video_action = QAction("Open Video", self)
        open_video_action.triggered.connect(self.open_video_dialog)

        # Create "Open GPS Data" action and connect it to the slot
        open_gpsdata_action = QAction("Open GPS Data", self)
        open_gpsdata_action.triggered.connect(self.open_gpsdata_dialog)

        restore_session_action = QAction("Restore Last Session", self)
        restore_session_action.triggered.connect(self.restore_session)

        # Create the "File" menu and add actions to it
        file_menu = menubar.addMenu("File")
        file_menu.addAction(open_video_action)
        file_menu.addAction(open_gpsdata_action)
        file_menu.addSeparator()
        file_menu.addAction(restore_session_action)

    @Slot()
    def open_video_dialog(self):
        """ prompts user for path of video """
        options = QFileDialog.Options()
        video_file, _ = QFileDialog.getOpenFileName(
            self, "Open Video File", "", "Video Files (*.mp4 *.avi *.mov)", options=options
            )
        if video_file:
            self.video_path = video_file
            return video_file
        raise NameError()

    @Slot()
    def open_gpsdata_dialog(self):
        """ prompts user for path of gps data """
        options = QFileDialog.Options()
        gps_data_file, _ = QFileDialog.getOpenFileName(
            self, "Open GPS Data File", "", "CSV Files (*.csv)", options=options
            )
        if gps_data_file:
            self.gps_data_path = gps_data_file
            return gps_data_file

    @Slot()
    def restore_session(self):
        """ slot for button, utilizes session """
        if self.session.load():
            # dummy setting variables to call setter and getter
            self.video_path = self.video_path
            self.gps_data_path = self.gps_data_path

    def import_button_clicked(self):
        """ Emit a Signal on button click """
        if self.check_path_validity():
            self.session.initialize(
                self.video_path,
                self.gps_data_path,
                None,
                None
            )
            self.import_requested.emit()

    def check_path_validity(self):
        """ checks if the given filepaths are valid and have a correct extension
        
        valid extensions can be modified via the lists 'valid_video_file_extensions'
        and 'valid_gpsdata_file_extensions'
        """
        if self.video_path is None or self.gps_data_path is None:
            return False
        if not os.path.exists(self.gps_data_path):
            return False
        if not any(self.gps_data_path.lower().endswith(ext) for ext in self.valid_gpsdata_file_extensions):
            return False
        if not os.path.exists(self.video_path):
            return False
        if not any(self.video_path.lower().endswith(ext) for ext in self.valid_video_file_extensions):
            return False
        return True

    @property
    def video_path(self) -> str:
        """ Getter for path to video file as str """
        return self.session.get("Video File Path")

    @video_path.setter
    def video_path(self, value) -> None:
        """ Setter for video_path, also updates textbox """
        self.video_path_textbox.setText(value)
        self.session.add("Video File Path", value)

    @property
    def gps_data_path(self) -> str:
        """ Getter for path to gps data file as str """
        return self.session.get("GPS Data Path")

    @gps_data_path.setter
    def gps_data_path(self, value) -> None:
        """ Setter for gps_data_path, also updates textbox """
        self.gps_data_path_textbox.setText(value)
        self.session.add("GPS Data Path", value)
