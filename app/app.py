import os
import threading
from datetime import datetime

from PyQt6 import QtGui
from PyQt6.QtWidgets import QMainWindow, QMessageBox
from PyQt6.uic import loadUi

from constants import *
from zkdevice import ZkDevice
from components import loading
import utils


STYLE_BTN = """
QPushButton {
    border: none; 
    border-radius: 5px;
    color: white; 
"""
DISABLE_CONNECT_BTN = STYLE_BTN + "background: rgba(0, 85, 255, 180);" + "}"
DISABLE_LIVE_CAPTURE_BTN = STYLE_BTN + "background: rgba(220, 53, 69, 180);" + "}"
ENABLE_LIVE_CAPTURE_BTN = STYLE_BTN + "background: rgba(220, 53, 69, 255);" + "}"


class App(QMainWindow):
    def __init__(self, odoosv=None):
        super().__init__()
        loadUi(os.path.join(UI_DIR, 'app.ui'), self)

        self.odoo_sv = odoosv
        self.devices = {}
        self.zkdevice = None
        self.print_total = 0
        self.loading_screen = loading.LoadingComponent()

        self.setWindowIcon(QtGui.QIcon(os.path.join(IMAGES_DIR, 'icon.ico')))
        self.connect_btn.clicked.connect(self.connect)
        self.live_capture_btn.clicked.connect(self.live_capture)
        self.live_capture_btn.setStyleSheet(DISABLE_LIVE_CAPTURE_BTN)
        self.live_capture_btn.setEnabled(False)

        if self.odoo_sv:
            self.get_devices()
            self.set_device_cb()

    def closeEvent(self, event):
        super(App, self).closeEvent()

    def get_devices(self):
        devices = self.odoo_sv.search(HR_MAYCHAMCONG_MODEL, [])
        if not devices:
            return
        for device in devices:
            device_name = device.get('name', str(device['id']))
            self.devices.update({device_name: device})

    def set_device_cb(self):
        if not self.devices:
            return
        device_names = self.devices.keys()
        self.device_cb.addItems(device_names)

    def connect(self):
        try:
            device_name = self.device_cb.currentText()
            if not device_name:
                return
            device = self.devices.get(device_name)
            ip = device.get('diachi_ip', '')
            port = device.get('port', '')
            port = int(port) if port else ''

            connection = ZkDevice(ip, port).connect()
            if connection:
                self.zkdevice = connection
                self.connect_btn.setStyleSheet(DISABLE_CONNECT_BTN)
                self.connect_btn.setEnabled(False)

                self.live_capture_btn.setEnabled(True)
                self.live_capture_btn.setStyleSheet(ENABLE_LIVE_CAPTURE_BTN)

                self.device_cb.setEnabled(False)
                QMessageBox.information(self, 'Thông báo', f'Kết nối thành công.')

        except Exception as e:
            QMessageBox.warning(self, 'Cảnh báo', f'Kết nối không thành công. \nLỗi: {e}')

    def show_loading(self):
        self.loading_screen.startAnimation()
        self.loading_screen.show()

    def set_print_total(self):
        now = datetime.now()
        now_str = now.strftime(YMD_FORMAT)
        query = [
            ('ngayan', '=', now_str),
            ('dain', '=', True)
        ]
        count = self.odoo_sv.count(HR_LUNCH_DANHSACH_MODEL, [query])
        self.print_total = 0
        if count and isinstance(count, int):
            self.print_total = count
        self._set_print_total()

    def _set_print_total(self):
        print_total_label = f"Tổng số phiếu in ngày hôm nay: {self.print_total}"
        self.print_total_label.setText(print_total_label)

    def live_capture(self):
        thread = threading.Thread(target=self._live_capture)
        thread.start()
        self.live_capture_btn.setStyleSheet(DISABLE_LIVE_CAPTURE_BTN)
        self.live_capture_btn.setEnabled(False)

    def _live_capture(self):
        try:
            print("_live_capture")
            self.set_print_total()
            zk = self.zkdevice

            for attendance in zk.live_capture(90):
                if attendance is None:
                    break
                machamcong = attendance.user_id
                timestamp = attendance.timestamp

                query = [
                    ('machamcong', '=', machamcong),
                    ('ngayan', '=', timestamp.strftime(YMD_FORMAT))
                ]
                record = self.odoo_sv.search(HR_LUNCH_DANHSACH_MODEL, [query])
                if not record:
                    self.set_info_and_create_log(log='Chưa đăng ký phần ăn cho hôm nay.', status=WARNING_STATUS, machamcong=machamcong)
                    continue
                record = record[0]
                kwargs = {
                    'name': record['display_name'] if record['display_name'] else '',
                    'machamcong': machamcong,
                    'manhanvien': record['manhanvien'] if record['manhanvien'] else '',
                    'company': record['company_id'][1] if record['company_id'] else '',
                    'department': record['department_id'][1] if record['department_id'] else '',
                    'status': WARNING_STATUS,
                }
                if not record['batdau'] or not record['ketthuc']:
                    self.set_info_and_create_log(log='Thời gian không hợp lệ.', **kwargs)
                    continue

                batdau = utils.convert_to_datetime_and_plus_7_hour(record['batdau'])
                ketthuc = utils.convert_to_datetime_and_plus_7_hour(record['ketthuc'])

                if timestamp < batdau or timestamp > ketthuc:
                    self.set_info_and_create_log(log='Không nằm trong thời gian cho phép.', **kwargs)
                    continue
                if record['dain']:
                    self.set_info_and_create_log(log='Đã in phiếu.', **kwargs)
                    continue

                # res = self.odoo_sv.update(HR_LUNCH_DANHSACH_MODEL, [record['id']], {'dain': True})
                # TODO: test, xóa res=True
                res = True

                if not res:
                    self.set_info_and_create_log(log='In phiếu không thành công.', **kwargs)
                    continue

                kwargs.update({'status': SUCCESS_STATUS})
                self.set_info_and_create_log(log='In phiếu thành công.', **kwargs)
                self.print_total += 1
                self._set_print_total()

        except Exception as e:
            self.set_info_and_create_log(log=f"Lỗi: {e}", status=ERROR_STATUS, log_type=HE_THONG_LOG_TYPE)
        finally:
            self.set_info()
            self._live_capture()

    def set_info_and_create_log(
            self,
            name='',
            machamcong='',
            company='',
            department='',
            log='',
            status='',
            log_type=IN_PHIEU_LOG_TYPE,
            manhanvien='',
    ):
        self.set_info(name, machamcong, company, department, log, status)

        # TODO: test, mở comment cho create_log
        # self.create_log(log, status, log_type, name, manhanvien, machamcong)

    def set_info(self, name='', machamcong='', company='', department='', log='', status=''):
        self.name_label.setText(name)
        self.machamcong_label.setText(machamcong)
        self.company_label.setText(company)
        self.department_label.setText(department)
        self.log_label.setText(log)
        if not status:
            return
        color = ''
        if status == SUCCESS_STATUS:
            color = 'green'
        if status == WARNING_STATUS:
            color = '#FFA000'
        if status == ERROR_STATUS:
            color = 'red'
        self.log_label.setStyleSheet(f"color: {color};")

    def create_log(self, log, status, log_type, tennhanvien='', manhanvien='', machamcong=''):
        now = datetime.now()
        now_str = utils.convert_to_str_and_minus_7_hour(now)
        data = {
            'name': log,
            'time': now_str,
            'status': status,
            'type': log_type,
            'tennhanvien': tennhanvien,
            'manhanvien': manhanvien,
            'machamcong': machamcong
        }
        self.odoo_sv.create(HR_LUNCH_LOGS_MODEL, [data])
