from datetime import datetime
from _mysql import OperationalError
from query import Query
from connection import Connection


READ_ONLY_MYSQL_STATUS = 'ON'
READ_WRITE_STATUS = 'read_write'
READ_ONLY_STATUS = 'read_only'
MYSQL_SERVER_STATUS_UP = 'Up'
MYSQL_SERVER_STATUS_DOWN = 'Down'
REPLICATION_STATUS_RUNNING = 'running'
REPLICATION_STATUS_STOPPED = 'stopped'
SLAVE_RUNNING_STATUS = 'Yes'


class LogicalNode(object):
    def __init__(self, group, ip, name, fox_connection):
        self.group = group
        self.ip = ip
        self.name = name
        self.address = self.format_server_name(ip, name)
        self.fox_connection = fox_connection

    def format_server_name(self, ip, name):
        return '{}({})'.format(name, ip)

    @property
    def fox_status(self):
        result = self.fox_connection.execute(
            Query.SQL_NODE_STATUS % (self.group, self.ip)
        )
        return result[0]['status']

    def is_enabled(self):
        return self.fox_status == 'enabled'

    def is_disabled(self):
        return self.fox_status == 'disabled'

    def is_failed(self):
        return self.fox_status == 'failed'

    @property
    def fox_mode(self):
        return self.fox_connection.execute(
            Query.SQL_NODE_STATUS % (self.group, self.ip)
        )[0]['mode']

    def is_fox_mode_read_only(self):
        return self.fox_mode == READ_ONLY_STATUS

    def is_fox_mode_read_write(self):
        return self.fox_mode == READ_WRITE_STATUS

    def __eq__(self, other):
        return (self.group == other.group and self.ip == other.ip)


class PhysicalNode(object):
    def __init__(self, ip, port, user, password, cipher):
        self.node_connection = Connection(ip, port, '', user, password, cipher)
        self.mysql_user = user
        self.mysql_password = password

    @property
    def mysql_status(self):
        try:
            with self.node_connection.connect():
                return MYSQL_SERVER_STATUS_UP
        except:
            return MYSQL_SERVER_STATUS_DOWN

    def is_mysql_status_up(self):
        return self.mysql_status == MYSQL_SERVER_STATUS_UP

    def is_mysql_status_down(self):
        return self.mysql_status == MYSQL_SERVER_STATUS_DOWN

    @property
    def mode(self):
        try:
            result = self.node_connection.execute(Query.SHOW_GLOBAL_STATUS_READ)[0]
        except OperationalError:
            return '-'
        else:
            if result['Value'] == READ_ONLY_MYSQL_STATUS:
                return READ_ONLY_STATUS
            return READ_WRITE_STATUS

    def is_read_only(self):
        return self.mode == READ_ONLY_STATUS

    def is_read_write(self):
        return self.mode == READ_WRITE_STATUS

    @property
    def replication_status(self):
        try:
            result = self.node_connection.execute(Query.SHOW_SLAVE_STATUS)[0]
        except OperationalError:
            return '-'
        else:
            is_io_running = result['Slave_IO_Running'] == SLAVE_RUNNING_STATUS
            is_sql_running = result['Slave_SQL_Running'] == SLAVE_RUNNING_STATUS
            if is_io_running and is_sql_running:
                return REPLICATION_STATUS_RUNNING
            return REPLICATION_STATUS_STOPPED

    def is_replication_stopped(self):
        return self.replication_status == REPLICATION_STATUS_STOPPED

    def is_replication_running(self):
        return self.replication_status == REPLICATION_STATUS_RUNNING

    @property
    def seconds_behind(self):
        try:
            result = self.node_connection.execute(Query.SQL_STATUS_HEARTBEAT)[0]
        except OperationalError:
            return '-'
        else:
            date_format = '%Y-%m-%d %H:%M:%S'
            now = datetime.now().replace(microsecond=0)

            heartbeat_time = datetime.strptime(
                result['last_update'], date_format
            )
            return (now - heartbeat_time).total_seconds()

    @property
    def master(self):
        try:
            result = self.node_connection.execute(Query.SHOW_SLAVE_STATUS)[0]
        except OperationalError:
            return None
        else:
            return result['Master_Host'] + ':' + str(result['Master_Port'])

    @property
    def server_id(self):
        try:
            result = self.node_connection.execute(Query.SHOW_GLOBAL_SERVER_ID)[0]
        except OperationalError:
            return None
        else:
            return int(result['Value'])

    @property
    def master_server_id(self):
        try:
            result = self.node_connection.execute(Query.SHOW_SLAVE_STATUS)[0]
        except OperationalError:
            return None
        else:
            return int(result['Master_Server_Id'])


class Node(LogicalNode, PhysicalNode):
    def __init__(self, group, ip, fox_connection):

        result = fox_connection.execute(Query.SQL_NODE_DETAILS % (group, ip))[0]

        LogicalNode.__init__(
            self, group, ip, result['servername'], fox_connection
        )
        PhysicalNode.__init__(
            self, ip, result['node_port'], result['mysql_adm_user'],
            fox_connection.cipher.decrypt(result['mysql_adm_pass']),
            fox_connection.cipher
        )

        self.port = result['node_port']

    def get_name_ip_port(self):
        return '{}({}:{})'.format(self.name, self.ip, self.port)
