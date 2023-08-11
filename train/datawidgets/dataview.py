from PySide6.QtWidgets import QWidget, QLabel, QTableWidget, QTableWidgetItem, QVBoxLayout, QHBoxLayout, QAbstractScrollArea, QPushButton

class DataViewWidget(QWidget):
    """ displays keyframe data and uses cameracalculation to calculate parameters """
    val = 0
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        """ initializes the ui """
        self.setWindowTitle("Data View")

        self.general_data_labels = [
            QLabel("Video File:"),
            QLabel("GPS Data:"),
            QLabel("Image Dimensions:"),
            QLabel("Track Gauge:")
        ]

        self.general_data_values = [
            QLabel(),
            QLabel(),
            QLabel(),
            QLabel()
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
        self.table.setRowCount(17)
        self.table.setVerticalHeaderLabels([
            "Timestamp", "Latitude", "Longitude", "Altitude", "Speed", # GPSDatum
            "Image Point A", "Image Point B", "Image Point C", "Image Point D", # Image ponts
            "Focal Length", "Principal Distance",
            "Swing", "Tilt", "Pan",
            "Height (Offset Z)", "Offset X", "Offset Y"
        ])

        self.table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)

        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_data)

        layout = QVBoxLayout()
        layout.addLayout(self.general_data_layout)
        layout.addWidget(self.table)
        layout.addWidget(save_button)

        self.setLayout(layout)

    def update_general_data(self, video_file, gps_data, image_dimension, track_gauge):
        """ updates the upper widget with general data """
        self.general_data_values[0].setText(video_file)
        self.general_data_values[1].setText(gps_data)
        self.general_data_values[2].setText(str(image_dimension))
        self.general_data_values[2].setText(track_gauge)

    def update_table(self, data):
        """ inserts a column behind average and calls average """
        col = self.table.columnCount()

        if col == 0:
            col = 1

        self.table.setColumnCount(col+1)
        self.table.setHorizontalHeaderLabels([*[str(i) for i in range(1, col+1)], "Average"])
        for row, value in enumerate(data):
            item = QTableWidgetItem(str(value))
            self.table.setItem(row, col-1, item)
        self.update_average()

    def update_average(self):
        """ calculates the average of relevant values and writes them into the last column """
        cc = self.table.columnCount()

        for row in range(self.table.rowCount()):
            value = "-"
            # only average calculated values
            if row > 8:
                column = [float(self.table.item(row, col).text()) for col in range(cc-1)]
                value = f"{sum(column)/len(column):.2f}"
            item = QTableWidgetItem(value)
            self.table.setItem(row, cc-1, item)


    def save_data(self):
        self.val += 1
        table_data = [123456, 37.7749, -122.4194, 50, 20, 100, 200, 300, 400, 45, 30, 60, 5, 3, 3, self.val, 5]
        self.update_table(table_data)

if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication

    app = QApplication([])
    main_window = DataViewWidget()
    main_window.update_general_data("video.mp4", "GPS Coordinates", [1920, 1080], "Standard Gauge")

    main_window.show()
    app.exec()
