""" Definition of DataViewWidget"""

from PySide6.QtWidgets import QWidget, QLabel, QTableWidget, QTableWidgetItem, QVBoxLayout, QHBoxLayout, QAbstractScrollArea, QPushButton

from COTabc import AbstractBaseWidget
from COTdataclasses import GPSDatum, KeyFrame


class DataViewWidget(AbstractBaseWidget):
    """ displays keyframe data and uses cameracalculation to calculate parameters """
    

    ################################## Implementation of abstract methods ###########################################

    def _initialize(self):
        pass

    def _setup_ui(self):
        """ initializes the ui """
        self._widget.setWindowTitle("Data View")

        self.general_data_labels = [
            QLabel("Video File:"),
            QLabel("GPS Data:"),
            QLabel("Image Dimensions:"),
            QLabel("Track Gauge:")
        ]

        self.general_data_values = [
            QLabel(self._session_handler.session_data.video_file_path.split("/")[-1]),
            QLabel(self._session_handler.session_data.video_file_path.split("/")[-1]),
            QLabel(
                f"{self._session_handler.session_data.image_width}, {self._session_handler.session_data.image_height}"
            ),
            QLabel("1435")
        ]

        self.general_data_layout = QVBoxLayout()
        for label, value in zip(self.general_data_labels, self.general_data_values):
            row_widget = QWidget()
            row_layout = QHBoxLayout()
            row_layout.addWidget(label)
            row_layout.addWidget(value)
            row_widget.setLayout(row_layout)
            self.general_data_layout.addWidget(row_widget)

        self.table = QTableWidget()
        self.table.setRowCount(19)
        self.table.setVerticalHeaderLabels([
            "Timestamp", "Time", "Latitude", "Longitude", "Altitude", "Speed", "Gradient", # GPSDatum
            "Image Point A", "Image Point B", "Image Point C", "Image Point D", # Image ponts
            "Focal Length", "Principal Distance",
            "Swing", "Tilt", "Pan",
            "Height (Offset Z)", "Offset X", "Offset Y"
        ])

        self.table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)

        # create save button and connect it to session handlers save function
        save_button = QPushButton("Save")
        save_button.clicked.connect(
            lambda: self._session_handler.save_keyframes(self._keyframe_handler)
        )

        # create layout
        layout = QVBoxLayout()
        layout.addLayout(self.general_data_layout)
        layout.addWidget(self.table)
        layout.addWidget(save_button)

        self._widget.setLayout(layout)
    
    def react_to_keyframe_change(self, keyframe: KeyFrame):
        self.update_table(keyframe)

    def react_to_gpsdatum_change(self, gpsdatum: GPSDatum):
        """ do nothing """


    ################################## Implementation of class methods ###########################################

    def update_table(self, keyframe: KeyFrame) -> None:
        """ updates the data table """
        col = 0
        col_max = self.table.columnCount()

        # if its the first keyframe, there is no column for average
        if col_max == 0:
            self.table.setColumnCount(2)
            self.table.setHorizontalHeaderLabels(["1", "Average"])
        else:
            for col in range(col_max - 1):
                # get the timestamp
                item: QTableWidgetItem = self.table.item(0, col)
                # if timestamp is already in the table, update the row
                if keyframe.gps.timestamp == int(item.text()):
                    break
            else:
                # happens anyway, but for clarification
                col = col_max - 1
                # insert a row at the end before average and change horizontal header labels
                self.table.insertColumn(col)
                # self.table.setHorizontalHeaderLabels([*[str(i) for i in range(1, col_max)], "Average"])
            
        # set data at determined
        self.update_column(col, keyframe)
        self.update_average()

    def update_column(self, col: int, keyframe: KeyFrame):
        # set gps datum
        if keyframe.gps is not None:
            self.table.setItem(
                0, col,
                QTableWidgetItem(f"{keyframe.gps.timestamp}")
            )
            self.table.setItem(
                1, col,
                QTableWidgetItem(f"{keyframe.gps.timeid}")
            )
            self.table.setItem(
                2, col,
                QTableWidgetItem(f"{keyframe.gps.latitude:.2f}")
            )
            self.table.setItem(
                3, col,
                QTableWidgetItem(f"{keyframe.gps.longitude:.2f}")
            )
            self.table.setItem(
                4, col,
                QTableWidgetItem(f"{keyframe.gps.altitude:.2f}")
            )
            self.table.setItem(
                5, col,
                QTableWidgetItem(f"{keyframe.gps.speed:.2f}")
            )
            self.table.setItem(
                6, col,
                QTableWidgetItem(f"{keyframe.gps.gradient:.2f}")
            )

        if keyframe.image_point is not None:
            self.table.setItem(
                7, col,
                QTableWidgetItem(str(keyframe.image_point.A))
            )
            self.table.setItem(
                8, col,
                QTableWidgetItem(str(keyframe.image_point.B))
            )
            self.table.setItem(
                9, col,
                QTableWidgetItem(str(keyframe.image_point.C))
            )
            self.table.setItem(
                10, col,
                QTableWidgetItem(str(keyframe.image_point.D))
            )
        if keyframe.intrinsics is not None:
            self.table.setItem(
                11, col,
                QTableWidgetItem(f"{keyframe.intrinsics.focal_length:.4f}")
            )
            self.table.setItem(
                12, col,
                QTableWidgetItem(f"{keyframe.intrinsics.principal_length:.4f}")
            )
        if keyframe.extrinsics is not None:
            self.table.setItem(
                13, col,
                QTableWidgetItem(f"{keyframe.extrinsics.swing:.4f}")
            )
            self.table.setItem(
                14, col,
                QTableWidgetItem(f"{keyframe.extrinsics.tilt:.4f}")
            )
            self.table.setItem(
                15, col,
                QTableWidgetItem(f"{keyframe.extrinsics.pan:.4f}")
            )
            self.table.setItem(
                16, col,
                QTableWidgetItem(f"{keyframe.extrinsics.z_offset:.4f}")
            )
            self.table.setItem(
                17, col,
                QTableWidgetItem(f"{keyframe.extrinsics.x_offset:.4f}")
            )
            self.table.setItem(
                18, col,
                QTableWidgetItem(f"{keyframe.extrinsics.y_offset:.4f}")
            )

    def update_average(self):
        """ calculates the average of relevant values and writes them into the last column """
        col_max = self.table.columnCount()

        for row in range(self.table.rowCount()):
            value = "-"
            # only average calculated values
            if row > 10:
                row_data = [float(self.table.item(row, col).text()) for col in range(col_max-1) if self.table.item(row, col) is not None]
                if len(row_data) > 0:
                    value = f"{sum(row_data)/len(row_data):.4f}"
            item = QTableWidgetItem(value)
            self.table.setItem(row, col_max-1, item)

if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    main_window = DataViewWidget()
    main_window.update_general_data("video.mp4", "GPS Coordinates", [1920, 1080], "Standard Gauge")

    main_window.show()
    app.exec()
