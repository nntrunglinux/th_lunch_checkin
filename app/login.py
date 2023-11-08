import json

from PyQt6 import QtGui
from PyQt6.QtWidgets import QMainWindow, QMessageBox
from PyQt6.uic import loadUi

from .app import App
from constants import *
from odoo_server import OdooServer


class Login(QMainWindow):
    def __init__(self):
        super(Login, self).__init__()
        loadUi(os.path.join(UI_DIR, 'login.ui'), self)

        self.app_window = App()
        self.login_btn.clicked.connect(self.login)
        self.setWindowIcon(QtGui.QIcon(os.path.join(IMAGES_DIR, 'icon.ico')))
        self.version_label.setText(f"Version: {VERSION}")
        self.load_login_info_from_login_json_file()

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
                self.write_login_info_from_login_json_file()
                self.app_window = App(odoosv)
                self.app_window.show()
                self.hide()
            else:
                QMessageBox.warning(self, 'Cảnh báo', f'Đăng nhập không thành công.')

        except Exception as e:
            QMessageBox.critical(self, 'Thất bại', f'Lỗi trong quá trình đăng nhập. \nLỗi: {e}')

    def write_login_info_from_login_json_file(self):
        host = self.host_lt.text()
        database = self.database_lt.text()
        username = self.username_lt.text()
        password = self.password_lt.text()
        data = {
            'host': host,
            'database': database,
            'username': username,
            'password': password,
        }
        with open(LOGIN_JSON_FILE_PATH, "w") as file:
            json.dump(data, file)

    def load_login_info_from_login_json_file(self):
        data = {}
        try:
            with open(LOGIN_JSON_FILE_PATH, "r") as file:
                json_data = json.load(file)
                if not json_data:
                    return
                if not isinstance(json_data, dict):
                    return
                data = json_data

        except Exception as e:
            print(f"Loi load login info. Loi: {e}")
            data = {}
        finally:
            self.host_lt.setText(data.get('host', ''))
            self.database_lt.setText(data.get('database', ''))
            self.username_lt.setText(data.get('username', ''))
            self.password_lt.setText(data.get('password', ''))
