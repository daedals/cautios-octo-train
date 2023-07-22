""" file picker """

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QFileDialog, QLabel
from PySide6.QtGui import QAction


class FilePickerApp(QMainWindow):
    """
    basic application for opening a file dialog by choosing the respective option in the menubar
    """

    _video_path: str
    _gps_data_path: str

    def __init__(self):
        super().__init__()

        # Create the main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)

        # Create the text boxes
        self.video_path_textbox = QLabel()
        self.gps_data_path_textbox = QLabel()

        # Add the text boxes to the layout
        main_layout.addWidget(self.video_path_textbox)
        main_layout.addWidget(self.gps_data_path_textbox)

        # Set the main widget
        self.setCentralWidget(main_widget)

        # Create the menu bar
        menubar = self.menuBar()

        # Create "Open Video" action and connect it to the slot
        open_video_action = QAction("Open Video", self)
        open_video_action.triggered.connect(self.open_video_dialog)

        # Create "Open GPS Data" action and connect it to the slot
        open_gps_data_action = QAction("Open GPS Data", self)
        open_gps_data_action.triggered.connect(self.open_gps_data_dialog)

        # Create the "File" menu and add actions to it
        file_menu = menubar.addMenu("File")
        file_menu.addAction(open_video_action)
        file_menu.addAction(open_gps_data_action)

    def open_video_dialog(self):
        """ prompts user for path of video """
        options = QFileDialog.Options()
        video_file, _ = QFileDialog.getOpenFileName(
            self, "Open Video File", "", "Video Files (*.mp4 *.avi *.mov)", options=options
            )
        if video_file:
            self._video_path = video_file
            self.video_path_textbox.setText(video_file)
            return video_file
        raise NameError()

    def open_gps_data_dialog(self):
        """ prompts user for path of gps data """
        options = QFileDialog.Options()
        gps_data_file, _ = QFileDialog.getOpenFileName(
            self, "Open GPS Data File", "", "CSV Files (*.csv)", options=options
            )
        if gps_data_file:
            self._gps_data_path = gps_data_file
            self.gps_data_path_textbox.setText(gps_data_file)

    @property
    def video_path(self) -> str:
        """ path to video file as str """
        return self._video_path

    @property
    def gps_data_path(self) -> str:
        """ path to gps data file as str """
        return self._gps_data_path


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FilePickerApp()
    window.show()
    sys.exit(app.exec())
