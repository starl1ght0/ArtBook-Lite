from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import (QMainWindow, QFileDialog, QApplication,
                            QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                            QLabel, QFrame, QColorDialog, QSlider, QButtonGroup,
                            QShortcut, QSizePolicy)

from Canvas import Canvas
from Window import Window


if __name__ == "__main__":
    App = QApplication([])
    window = Window()
    window.show()
    App.exec()
