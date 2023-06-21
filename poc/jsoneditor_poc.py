import sys
import json
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit
from PyQt6.QtCore import QFile


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("JSON Editor")

        self.json_data = {}

        self.load_json()
        self.setup_ui()

    def load_json(self):
        try:
            with open("data.json", "r") as file:
                self.json_data = json.load(file)
        except FileNotFoundError:
            # If the file doesn't exist, create an empty JSON object
            self.json_data = {}

    def save_json(self):
        with open("data.json", "w") as file:
            json.dump(self.json_data, file, indent=4)

    def setup_ui(self):
        # Create a central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create a layout
        layout = QVBoxLayout(central_widget)

        # Create a label
        label = QLabel("Name:")
        layout.addWidget(label)

        # Create a line edit
        line_edit = QLineEdit()
        line_edit.setText(self.json_data.get("name", ""))
        layout.addWidget(line_edit)

        # Connect the line edit text changed signal to update the JSON data
        line_edit.textChanged.connect(lambda text: self.json_data.update({"name": text}))

    def closeEvent(self, event):
        # Save the JSON data before closing the application
        self.save_json()
        event.accept()


# Create the application instance
app = QApplication(sys.argv)

# Create the main window
window = MainWindow()
window.show()

# Run the event loop
sys.exit(app.exec())