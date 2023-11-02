import sys
from PyQt6.QtWidgets import QApplication
from app import login


def main():
    q_app = QApplication(sys.argv)
    login_window = login.Login()
    login_window.show()
    sys.exit(q_app.exec())


if __name__ == "__main__":
    main()
