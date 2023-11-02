from contextlib import contextmanager
from zk import ZK


@contextmanager
def zk_connect(device: ZK):
    try:
        conn = device.connect()
        yield conn
    except Exception as e:
        raise e
    else:
        conn.disconnect()


class ZkDevice:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.zk = ZK(ip, port)

    def connect(self):
        # connection = None
        try:
            connection = self.zk.connect()
            return connection
            # self.zk.disconnect()
        except Exception as e:
            raise e
        # finally:
        #     return connection

    def load_users(self):
        users = []
        with zk_connect(self.zk) as conn:
            users = conn.get_users()
        return users

    def load_attendances(self):
        attendances = []
        with zk_connect(self.zk) as conn:
            attendances = conn.get_attendance()
        return attendances

    def load_fingers(self):
        fingers = []
        with zk_connect(self.zk) as conn:
            fingers = conn.get_templates()
        return fingers
