import xmlrpc.client
from dataclasses import dataclass


@dataclass
class OdooServer:
    url: str
    db: str
    username: str
    password: str
    common = None
    proxy = None
    uid = None

    def __post_init__(self):
        self.common = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/common")
        self.proxy = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/object")

    def connect(self):
        try:
            self.uid = self.common.authenticate(
                self.db, self.username, self.password, {}
            )
        except Exception as e:
            raise e
        finally:
            return self.uid

    def _execute(self, model, method, query=None, params=None):
        if not query:
            query = []
        if not params:
            params = {}
        try:
            return self.proxy.execute_kw(
                self.db, self.uid, self.password, model, method, query, params
            )
        except Exception as e:
            return False

    def search(self, model, query=None, params=None):
        """Return list of dictionary records"""
        return self._execute(model, "search_read", query, params)

    def find(self, model, query=None, params=None):
        """Return list of ids"""
        return self._execute(model, "search", query, params)

    def count(self, model, query=None):
        """Return count of records in model"""
        return self._execute(model, "search_count", query)

    def create(self, model, data):
        """Return list of ids"""
        return self._execute(model, "create", data)

    def delete(self, model, data):
        """Return bool"""
        return self._execute(model, "unlink", data)

    def update(self, model, ids: list, data: dict):
        """Return bool"""
        try:
            return self.proxy.execute_kw(
                self.db, self.uid, self.password, model, "write", [ids, data]
            )
        except Exception as e:
            # logger.error(e)
            return False
