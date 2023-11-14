import threading
import time
from datetime import datetime, timedelta
import pandas as pd

from PyQt6 import QtGui
from PyQt6.QtWidgets import QMainWindow, QMessageBox, QTableWidgetItem, QVBoxLayout, QGroupBox, QLabel
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
ENABLE_CONNECT_BTN = STYLE_BTN + "background: rgb(0, 85, 255);" + "}"
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
        self.lunch_info_list = []
        self.loading_screen = loading.LoadingComponent()

        self.setWindowIcon(QtGui.QIcon(os.path.join(IMAGES_DIR, 'icon.ico')))
        self.connect_btn.clicked.connect(self.connect_and_live_capture)

        self.get_lunch_by_condition_btn.clicked.connect(self.get_lunch_by_condition)
        self.from_dateedit.setDate(datetime.now().date())
        self.to_dateedit.setDate(datetime.now().date())

        self.lunch_table.setColumnWidth(0, 400)
        self.lunch_table.setColumnWidth(1, 200)
        self.lunch_table.setColumnWidth(2, 145)

        self.export_excel_lunch_btn.clicked.connect(self.export_excel)

        # LUNCH ITEM 1
        self.name_info_label1 = QLabel(f"Họ tên: ")
        self.machamcong_info_label1 = QLabel(f"Mã chấm công: ")
        self.company_info_label1 = QLabel(f"Công ty: ")
        self.department_info_label1 = QLabel(f"Phòng ban: ")

        self.lunch_info_item1 = QGroupBox()
        self.layout1 = QVBoxLayout()
        self.layout1.addWidget(self.name_info_label1)
        self.layout1.addWidget(self.machamcong_info_label1)
        self.layout1.addWidget(self.company_info_label1)
        self.layout1.addWidget(self.department_info_label1)
        self.lunch_info_item1.setTitle('Hoàn thành')
        self.lunch_info_item1.setLayout(self.layout1)

        # LUNCH ITEM 2
        self.name_info_label2 = QLabel(f"Họ tên: ")
        self.machamcong_info_label2 = QLabel(f"Mã chấm công: ")
        self.company_info_label2 = QLabel(f"Công ty: ")
        self.department_info_label2 = QLabel(f"Phòng ban: ")

        self.lunch_info_item2 = QGroupBox()
        self.layout2 = QVBoxLayout()
        self.layout2.addWidget(self.name_info_label2)
        self.layout2.addWidget(self.machamcong_info_label2)
        self.layout2.addWidget(self.company_info_label2)
        self.layout2.addWidget(self.department_info_label2)
        self.lunch_info_item2.setTitle('Hoàn thành')
        self.lunch_info_item2.setLayout(self.layout2)

        # LUNCH ITEM 3
        self.name_info_label3 = QLabel(f"Họ tên: ")
        self.machamcong_info_label3 = QLabel(f"Mã chấm công: ")
        self.company_info_label3 = QLabel(f"Công ty: ")
        self.department_info_label3 = QLabel(f"Phòng ban: ")

        self.lunch_info_item3 = QGroupBox()
        self.layout3 = QVBoxLayout()
        self.layout3.addWidget(self.name_info_label3)
        self.layout3.addWidget(self.machamcong_info_label3)
        self.layout3.addWidget(self.company_info_label3)
        self.layout3.addWidget(self.department_info_label3)
        self.lunch_info_item3.setTitle('Hoàn thành')
        self.lunch_info_item3.setLayout(self.layout3)

        # LUNCH LIST
        self.lunch_info_layout.addWidget(self.lunch_info_item1)
        self.lunch_info_layout.addWidget(self.lunch_info_item2)
        self.lunch_info_layout.addWidget(self.lunch_info_item3)
        self.lunch_info_layout.addStretch()
        self.lunch_info_widget.setLayout(self.lunch_info_layout)
        self.lunch_info_widget.setStyleSheet("QLabel {font-size: 11pt;}")

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

    def _live_capture(self):
        try:
            print("_live_capture")
            self.set_print_total()
            zk = self.zkdevice

            for attendance in zk.live_capture(90):
                print(f"connect: {self.zkdevice.is_connect} - end_live_capture: {self.zkdevice.end_live_capture}")
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

                res = self.odoo_sv.update(HR_LUNCH_DANHSACH_MODEL, [record['id']], {'dain': True})
                if not res:
                    self.set_info_and_create_log(log='In phiếu không thành công.', **kwargs)
                    continue

                kwargs.update({'status': SUCCESS_STATUS})
                self.set_info_and_create_log(log='In phiếu thành công.', **kwargs)
                self.print_total += 1
                self._set_print_total()

        except Exception as e:
            self.set_info_and_create_log(log=f"Lỗi: {e}", status=ERROR_STATUS, log_type=HE_THONG_LOG_TYPE)
            print(f"Loi trong luc xu ly in phieu. Loi: {e}")
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
        self.create_log(log, status, log_type, name, manhanvien, machamcong)

    def set_info(self, name='', machamcong='', company='', department='', log='', status=''):
        try:
            self.name_label.setText(name)
            self.machamcong_label.setText(machamcong)
            self.company_label.setText(company)
            self.department_label.setText(department)
            self.log_label.setText(log)
            if not status:
                return
            color = ''
            status_text = ''
            if status == SUCCESS_STATUS:
                color = 'green'
                status_text = 'Hoàn thành'
            if status == WARNING_STATUS:
                color = '#FFA000'
                status_text = 'Cảnh báo'
            if status == ERROR_STATUS:
                color = 'red'
                status_text = 'Lỗi'
            self.log_label.setStyleSheet(f"color: {color};")

            self.lunch_info_list = self.lunch_info_list[0:2]
            self.lunch_info_list.insert(0, {
                'name': name,
                'machamcong': machamcong,
                'company': company,
                'department': department,
                'status': status_text,
                'color': color,
            })
            self.add_item_for_lunch_info_list()
        except Exception as e:
            raise Exception(f"Loi thiet lap thong tin: {e}")

    def create_log(self, log, status, log_type, tennhanvien='', manhanvien='', machamcong=''):
        try:
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
        except Exception as e:
            raise Exception(f"Loi tao log: {e}")

    def get_lunch_by_condition(self):
        self.lunch_status_label.setText('Trạng thái:')
        self.lunch_status_label.setStyleSheet('color: black;')
        self.export_excel_lunch_btn.setStyleSheet(DISABLE_LIVE_CAPTURE_BTN)
        self.export_excel_lunch_btn.setEnabled(False)
        self.show_loading()
        thread = threading.Thread(target=self._get_lunch_by_condition)
        thread.start()

    def _get_lunch_by_condition(self):
        try:
            self.lunch_table.setRowCount(0)
            from_date = self.from_dateedit.date().toPyDate()
            to_date = self.to_dateedit.date().toPyDate()

            if from_date > to_date:
                QMessageBox.warning(self, 'Cảnh báo', f'Từ ngày không thể lớn hơn đến ngày.')
                return

            days_total = (to_date - from_date).days + 1
            companies = self.odoo_sv.search(RES_COMPANY_MODEL, [], {'fields': ['name']})
            self.lunch_table.setRowCount(days_total * len(companies))
            row = 0
            company_ids = [company['id'] for company in companies]
            query = [
                ('ngayan', '>=', from_date.strftime(YMD_FORMAT)),
                ('ngayan', '<=', to_date.strftime(YMD_FORMAT)),
                ('company_id', 'in', company_ids),
                ('dain', '=', True)
            ]
            records = self.odoo_sv.search(HR_LUNCH_DANHSACH_MODEL, [query], {'fields': ['ngayan', 'company_id']})
            self.lunch_total_label.setText(f"Tổng: {str(len(records))}")
            time.sleep(0.02)

            for day in range(days_total):
                day_condition = from_date + timedelta(days=day)
                day_condition_str = day_condition.strftime(YMD_FORMAT)
                for company in companies:
                    filtered_records = filter(
                        lambda r: (r['company_id'][0] == company['id']) and r['ngayan'] == day_condition_str, records
                    )
                    filtered_records = list(filtered_records)
                    if not filtered_records:
                        continue
                    total_filtered_records = str(len(filtered_records))
                    self.lunch_table.setItem(row, 0, QTableWidgetItem(company['name']))
                    self.lunch_table.setItem(row, 1, QTableWidgetItem(day_condition_str))
                    self.lunch_table.setItem(row, 2, QTableWidgetItem(total_filtered_records))
                    time.sleep(0.02)
                    row += 1

            self.loading_screen.stopAnimation()
            self.export_excel_lunch_btn.setStyleSheet(ENABLE_LIVE_CAPTURE_BTN)
            self.export_excel_lunch_btn.setEnabled(True)
            self.lunch_status_label.setText(f"Trạng thái: lấy dữ liệu thành công.")
            self.lunch_status_label.setStyleSheet('color: green;')

        except Exception as e:
            self.loading_screen.stopAnimation()
            self.export_excel_lunch_btn.setStyleSheet(ENABLE_LIVE_CAPTURE_BTN)
            self.export_excel_lunch_btn.setEnabled(True)
            self.lunch_status_label.setText(f"Trạng thái: lấy dữ liệu không thành công. {e}")
            self.lunch_status_label.setStyleSheet('color: red;')

    def export_excel(self):
        self.lunch_status_label.setText('Trạng thái:')
        self.lunch_status_label.setStyleSheet('color: black;')
        self.get_lunch_by_condition_btn.setStyleSheet(DISABLE_CONNECT_BTN)
        self.get_lunch_by_condition_btn.setEnabled(False)
        self.show_loading()
        thread = threading.Thread(target=self._export_excel)
        thread.start()

    def _export_excel(self):
        try:
            time.sleep(1)
            row_count = self.lunch_table.rowCount()
            column_count = 3
            headers = ['Công ty', 'Ngày ăn', 'Tổng']
            data = []

            for row in range(row_count):
                row_data = []
                for column in range(column_count):
                    widget_item = self.lunch_table.item(row, column)
                    if not widget_item or not widget_item.text():
                        continue
                    row_data.append(widget_item.text())
                if row_data:
                    data.append(row_data)

            if data:
                df = pd.DataFrame(data)
                df.to_excel('danh_sach_phan_an.xlsx', header=headers, index=False)

            time.sleep(1)
            self.loading_screen.stopAnimation()
            self.get_lunch_by_condition_btn.setStyleSheet(ENABLE_CONNECT_BTN)
            self.get_lunch_by_condition_btn.setEnabled(True)
            self.lunch_status_label.setText(f"Trạng thái: xuất excel thành công.")
            self.lunch_status_label.setStyleSheet('color: green;')

        except Exception as e:
            self.loading_screen.stopAnimation()
            self.get_lunch_by_condition_btn.setStyleSheet(ENABLE_CONNECT_BTN)
            self.get_lunch_by_condition_btn.setEnabled(True)
            self.lunch_status_label.setText(f"Trạng thái: lỗi trong quá trình xuất excel. {e}")
            self.lunch_status_label.setStyleSheet('color: red;')

    def connect_and_live_capture(self):
        self.connect()
        if not self.zkdevice or self.zkdevice is None:
            return
        self.live_capture()

    def add_item_for_lunch_info_list(self):
        print('add_item_for_lunch_info_list running')
        if not self.lunch_info_list:
            return
        list_length = len(self.lunch_info_list)
        print(f"List length: {list_length}")

        for i in range(list_length):
            item = self.lunch_info_list[i]
            if i == 0:
                status = item['status']
                self.name_info_label1.setText(f"Họ tên: {item['name']}")
                self.machamcong_info_label1.setText(f"Mã chấm công: {item['machamcong']}")
                self.company_info_label1.setText(f"Công ty: {item['company']}")
                self.department_info_label1.setText(f"Phòng ban: {item['department']}")
                self.lunch_info_item1.setStyleSheet(f"color: {item['color']}")
                self.lunch_info_item1.setTitle(status)

            if i == 1:
                status = item['status']
                self.name_info_label2.setText(f"Họ tên: {item['name']}")
                self.machamcong_info_label2.setText(f"Mã chấm công: {item['machamcong']}")
                self.company_info_label2.setText(f"Công ty: {item['company']}")
                self.department_info_label2.setText(f"Phòng ban: {item['department']}")
                self.lunch_info_item2.setStyleSheet(f"color: {item['color']}")
                self.lunch_info_item2.setTitle(status)

            if i == 2:
                status = item['status']
                self.name_info_label3.setText(f"Họ tên: {item['name']}")
                self.machamcong_info_label3.setText(f"Mã chấm công: {item['machamcong']}")
                self.company_info_label3.setText(f"Công ty: {item['company']}")
                self.department_info_label3.setText(f"Phòng ban: {item['department']}")
                self.lunch_info_item3.setStyleSheet(f"color: {item['color']}")
                self.lunch_info_item3.setTitle(status)