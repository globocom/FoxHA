from contextlib import contextmanager
import _mysql as MySQLdb
import MySQLdb.cursors
from utils import Utils


def from_config_file(cipher=None, config_path=None):
    if not cipher:
        cipher = Utils.parse_key_file(Utils.get_key_path())

    if not config_path:
        config_path = Utils.get_config_path()

    connection_params = Utils.parse_config_file(cipher, config_path)
    return Connection(*connection_params, cipher=cipher)


class Connection(object):
    def __init__(self, host, port, database, user, password, cipher):
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.cipher = cipher

    @contextmanager
    def connect(self):
        client = None
        try:
            client = MySQLdb.connect(
                host=self.host, port=self.port, user=self.user,
                passwd=self.password, db=self.database, connect_timeout=5,
                cursorclass=MySQLdb.cursors.DictCursor, compress=1
            )
            yield client
        finally:
            if client:
                client.close()

    def execute(self, sql_statement):
        with self.connect() as client:
            client.query(sql_statement)
            result = client.store_result()
            if result:
                return result.fetch_row(maxrows=0, how=1)

    def query(self, sql_statement):
        with self.connect() as client:
            client.query(sql_statement)
            client.commit()
