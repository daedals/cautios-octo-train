import sys
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6 import uic

import qdarktheme

class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi("cotui/cotui-main.ui", self)


app = QtWidgets.QApplication(sys.argv)

qdarktheme.setup_theme()

window = MainWindow()
window.show()
app.exec()