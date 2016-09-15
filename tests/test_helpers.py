import socket
import time
import paramiko
import ConfigParser
from foxha.utils import Utils


class EnvironmentNode(object):
    def __init__(self, address, user, password, port=22):
        self.address = address
        self.user = user
        self.password = password
        self.port = port


class BuildEnvironment(object):
    def __init__(self, path, keyfile):
        config = ConfigParser.ConfigParser()
        config.read(path)

        self.group = config.get('env', 'group')
        self.description = config.get('env', 'description')
        self.vip_address = config.get('env', 'vip_address')
        self.mysql_adm_user = config.get('env', 'master_mysql_user')
        self.mysql_repl_user = config.get('env', 'slave_mysql_user')

        self.master = config.get('env', 'master')
        self.replication = config.get('env', 'slave')

        cipher = Utils.parse_key_file(keyfile)
        self.master_node = EnvironmentNode(
            self.master,
            config.get('env', 'master_ssh_user'),
            cipher.decrypt(config.get('env', 'master_ssh_password')),
            config.get('env', 'master_ssh_port')
        )
        self.replication_node = EnvironmentNode(
            self.replication,
            config.get('env', 'slave_ssh_user'),
            cipher.decrypt(config.get('env', 'slave_ssh_password')),
            config.get('env', 'slave_ssh_port')
        )

        self.nodes = []
        self.nodes.append(self.master_node)
        self.nodes.append(self.replication_node)


class RemoteHostInterface(object):
    def __init__(self, host, user, password, port=22):
        self._host = host
        self._user = user
        self._password = password
        self.__ssh_client = self.__get_ssh_client()
        self._port = int(port)

    def __get_ssh_client(self,):
        return paramiko.SSHClient()

    def __establish_ssh_connection(self):
        self.__ssh_client.connect(
            self._host, username=self._user, password=self._password, port=self._port
        )

    def __close_ssh_connection(self):
        self.__ssh_client.close()

    def __handle_ssh_keys(self):
        #self.__ssh_client.load_system_host_keys()
        self.__ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def __exec_remote_command(self, command):
        return self.__ssh_client.exec_command(command)

    def __get_connection_exception_handlers(self):
        return (
            paramiko.ssh_exception.AuthenticationException, socket.error,
            paramiko.ssh_exception.SSHException,
            paramiko.ssh_exception.BadHostKeyException,
            paramiko.ssh_exception.NoValidConnectionsError
        )

    def _exec_remote_command(
        self, command, max_connection_retry=1000, wait_between_retires=10
    ):
        self.__handle_ssh_keys()
        exception_handlers = self.__get_connection_exception_handlers()
        for attempt in xrange(max_connection_retry):
            try:
                self.__establish_ssh_connection()
            except exception_handlers:
                time.sleep(wait_between_retires)
            else:
                break

        return self.__exec_remote_command(command)

    def _handle_command_output(self, stdout_handler, stderr_handler):
        exit_status = stdout_handler.channel.recv_exit_status()
        log_stdout = stdout_handler.read()
        log_stderr = stderr_handler.read()

        return exit_status, log_stdout, log_stderr

    def exec_remote_command(self, command):
        _, stdout, stderr = self._exec_remote_command(command)

        if not stdout and not stderr:
            raise Exception(
                'Unable to establish a connection with: {}'.format(self._host)
            )

        return self._handle_command_output(stdout, stderr)
