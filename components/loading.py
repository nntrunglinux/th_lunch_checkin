import os

from PyQt6 import QtCore
from PyQt6.QtWidgets import QLabel, QWidget

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QMovie
from constants import IMAGES_DIR


class LoadingComponent(QWidget):
    def __init__(self):
        super().__init__()
        # self.setFixedSize(142, 142)
        self.setFixedSize(200, 200)

        self.label_animation = QLabel(self)
        self.movie = QMovie(os.path.join(IMAGES_DIR, 'loading1.gif'))
        self.label_animation.setMovie(self.movie)

        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)

    def show_loading_gif(self):
        timer = QTimer(self)
        self.startAnimation()
        timer.singleShot(1000, self.stopAnimation)
        self.show()

    def startAnimation(self):
        self.movie.start()

    def stopAnimation(self):
        self.movie.stop()
        # self.close()
        self.hide()
