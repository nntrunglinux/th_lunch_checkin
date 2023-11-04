import os

from PyQt6 import QtGui
from PyQt6.QtWidgets import QMainWindow, QMessageBox
from PyQt6.uic import loadUi

from .app import App
from constants import APP_DIR, IMAGES_DIR, VERSION, UI_DIR
from odoo_server import OdooServer


class Login(QMainWindow):
    def __init__(self):
        super(Login, self).__init__()
        loadUi(os.path.join(UI_DIR, 'login.ui'), self)

        self.app_window = App()
        self.login_btn.clicked.connect(self.login)
        self.setWindowIcon(QtGui.QIcon(os.path.join(IMAGES_DIR, 'icon.ico')))
        self.version_label.setText(f"Version: {VERSION}")

    def login(self):
        host = self.host_lt.text()
        database = self.database_lt.text()
        username = self.username_lt.text()
        password = self.password_lt.text()
        if not(host and database and username and password):
            QMessageBox.warning(self, 'Cảnh báo', 'Thông tin không đầy đủ.')
            return

        try:
            odoosv = OdooServer(host, database, username, password)
            uid = odoosv.connect()
            if uid:
                # self.app_window.showMaximized()
                self.app_window = App(odoosv)
                self.app_window.show()
                self.hide()
            else:
                QMessageBox.warning(self, 'Cảnh báo', f'Đăng nhập không thành công.')

        except Exception as e:
            QMessageBox.critical(self, 'Thất bại', f'Lỗi trong quá trình đăng nhập. \nLỗi: {e}')
