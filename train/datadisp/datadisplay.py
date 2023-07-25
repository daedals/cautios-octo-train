from PySide6.QtWidgets import QApplication, QLabel, QFormLayout, QVBoxLayout, QWidget, QLineEdit
import sys


class DataViewWidget(QWidget):
    def __init__(self):
        super().__init__()

        # Set up the UI
        layout = QVBoxLayout()

        # General Data Section
        general_data_label = QLabel("General Data")
        self.frame_label = QLabel()
        self.time_label = QLabel()
        self.latitude_label = QLabel()
        self.longitude_label = QLabel()
        self.altitude_label = QLabel()
        self.speed_label = QLabel()

        # Create a QFormLayout for the general data section
        form_layout = QFormLayout()
        form_layout.addRow("Frame:", self.frame_label)
        form_layout.addRow("Time:", self.time_label)
        form_layout.addRow("Latitude:", self.latitude_label)
        form_layout.addRow("Longitude:", self.longitude_label)
        form_layout.addRow("Altitude:", self.altitude_label)
        form_layout.addRow("Speed:", self.speed_label)

        # Supplied Image Coordinates Section
        supplied_image_coords_label = QLabel("Supplied Image Coordinates")
        self.supplied_image_coords_table = QFormLayout()

        # Measured World Dimensions Section
        measured_world_dims_label = QLabel("Measured World Dimensions")
        self.height_edit = QLineEdit()
        self.width_edit = QLineEdit()

        # Intrinsic and Extrinsic Parameters Section
        intrinsic_extrinsic_label = QLabel("Intrinsic and Extrinsic Parameters")
        self.intrinsic_extrinsic_table = QFormLayout()

        # Add all sections to the layout
        layout.addWidget(general_data_label)
        layout.addLayout(form_layout)
        layout.addWidget(supplied_image_coords_label)
        layout.addLayout(self.supplied_image_coords_table)
        layout.addWidget(measured_world_dims_label)
        layout.addWidget(self.height_edit)
        layout.addWidget(self.width_edit)
        layout.addWidget(intrinsic_extrinsic_label)
        layout.addLayout(self.intrinsic_extrinsic_table)

        # Set the main layout
        self.setLayout(layout)

        # Set initial data
        self.update_general_data(None)
        self.update_supplied_image_coords([])
        self.update_measured_world_dims(0, 0)
        self.update_intrinsic_extrinsic([])

    def update_general_data(self, data):
        # Function to update the General Data section
        if data is not None:
            self.frame_label.setText(str(data.get("frame", "")))
            self.time_label.setText(str(data.get("time", "")))
            self.latitude_label.setText(str(data.get("latitude", "")))
            self.longitude_label.setText(str(data.get("longitude", "")))
            self.altitude_label.setText(str(data.get("altitude", "")))
            self.speed_label.setText(str(data.get("speed", "")))
        else:
            # Clear the labels if there is no data
            self.frame_label.setText("")
            self.time_label.setText("")
            self.latitude_label.setText("")
            self.longitude_label.setText("")
            self.altitude_label.setText("")
            self.speed_label.setText("")

    def update_supplied_image_coords(self, data):
        # Function to update the Supplied Image Coordinates section
        for i in reversed(range(self.supplied_image_coords_table.count())):
            self.supplied_image_coords_table.itemAt(i).widget().setParent(None)

        for point, x, y in data:
            label = QLabel(f"Point {point}: ({x}, {y})")
            self.supplied_image_coords_table.addRow(label)

    def update_measured_world_dims(self, height, width):
        # Function to update the Measured World Dimensions section
        self.height_edit.setText(str(height))
        self.width_edit.setText(str(width))

    def update_intrinsic_extrinsic(self, data):
        # Function to update the Intrinsic and Extrinsic Parameters section
        for i in reversed(range(self.intrinsic_extrinsic_table.count())):
            self.intrinsic_extrinsic_table.itemAt(i).widget().setParent(None)

        for parameter, *values in data:
            label = QLabel(f"{parameter}: {', '.join(map(str, values))}")
            self.intrinsic_extrinsic_table.addRow(label)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DataViewWidget()
    window.show()

    # Example data (replace with your own data)
    general_data = {
        "frame": 1,
        "time": "12:30:45",
        "latitude": 51.234,
        "longitude": 10.987,
        "altitude": 100.5,
        "speed": 20.3
    }

    supplied_image_coords = [
        ["1", 100, 200],
        ["2", 150, 250],
        ["3", 180, 220],
        ["4", 130, 270],
    ]

    intrinsic_extrinsic_params = [
        ["Param 1", 1.0, 2.0, 3.0, 4.0, 5.0],
        ["Param 2", 0.5, 1.5, 2.5, 3.5, 4.5],
        # Add more parameter rows as needed
    ]

    window.update_general_data(general_data)
    window.update_supplied_image_coords(supplied_image_coords)
    window.update_measured_world_dims(100, 200)
    window.update_intrinsic_extrinsic(intrinsic_extrinsic_params)

    sys.exit(app.exec())
