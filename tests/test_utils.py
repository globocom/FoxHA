import re
import pytest
import time
from foxha import fox
from foxha import formatter
import conftest
from test_helpers import RemoteHostInterface


MYSQL_STOP_CMD = '/etc/init.d/mysql stop'
MYSQL_START_CMD = '/etc/init.d/mysql start'
MYSQL_RESTART_CMD = '/etc/init.d/mysql restart'


def __get_name(node):
    return re.search('.*(\()', node.strip()).group(0)[:-1]


def __get_ip(node):
    ip = re.search('(\().*', node.strip()).group(0)[1:-1]
    if re.search('.*(\:)', ip):
        ip = re.search('.*(\:)', ip).group(0)[:-1]
    return ip


def is_node_in_line(node_ip, line):
    values = line.split('|')
    if len(values) > 2:
        return node_ip in values[2]
    return False


def remove_ansi_format(string):
    return re.sub(r'\x1b[^m]*m', '', str(string.strip()))


def get_node_from_list(node_ip, capsys, group=None):
    if not group:
        group = conftest.environment().group

    with pytest.raises(SystemExit) as exec_info:
        formatter.list_nodes(group, conftest.default_connection())
    assert str(exec_info.value) == '0'

    out, err = capsys.readouterr()
    for line in out.split('\n'):
        if is_node_in_line(node_ip, line):
            data = line
            break

    group, address, status = data.split('|')[1:4]
    ip = __get_ip(address)
    name = __get_name(address)
    status = remove_ansi_format(status)

    return {'group': group.strip(), 'name': name.strip(),
            'ip': ip.strip(), 'status': status}


def __change_node_status(node_ip, group, status, capsys):
    node = get_node_from_list(node_ip, capsys, group)
    if node['status'] != status:
        fox.set(status, node['group'], node['ip'])
        node = get_node_from_list(node_ip, capsys, group)
    return node


def disable_node(node_ip, capsys, group=None):
    return __change_node_status(node_ip, group, 'disabled', capsys)


def enable_node(node_ip, capsys, group=None):
    return __change_node_status(node_ip, group, 'enabled', capsys)


def failed_node(node_ip, capsys, group=None):
    return __change_node_status(node_ip, group, 'failed', capsys)


def get_node_from_status(node_ip, capsys, group=None):
    if not group:
        group = conftest.environment().group
    formatter.status_nodes(
        group, conftest.default_logger(), conftest.default_connection()
    )

    out, err = capsys.readouterr()
    for line in out.split('\n'):

        if is_node_in_line(node_ip, line):
            data = line
            break

    group, address, status, mode, repl_status = data.split('|')[1:6]
    ip = __get_ip(address)
    name = __get_name(address)
    status = remove_ansi_format(status)

    return {
        'group': group.strip(),
        'name': name.strip(),
        'ip': ip.strip(),
        'status': status,
        'mode': mode.strip(),
        'repl_status': repl_status.strip()
    }


def __change_node_mode(node_ip, group, mode, capsys):
    node = get_node_from_status(node_ip, capsys, group)
    if node['mode'] != mode:
        fox.set(mode, node['group'], node['ip'])
        node = get_node_from_status(node_ip, capsys, group)
    return node


def set_read_only(node_ip, capsys, group=None):
    return __change_node_mode(node_ip, group, 'read_only', capsys)


def set_read_write(node_ip, capsys, group=None):
    return __change_node_mode(node_ip, group, 'read_write', capsys)


def reset_database():
    environment = conftest.environment()

    fox.set('enabled', environment.group, environment.master)
    fox.set('enabled', environment.group, environment.replication)
    fox.set('read_only', environment.group, environment.replication)
    fox.set('read_write', environment.group, environment.master)


def connect_database():
    fox.CONNECTION = conftest.default_connection()
    fox.LOGGER = conftest.default_logger()


def activate_nodes():
    environment = conftest.environment()
    __execute_command_in_nodes(environment, MYSQL_RESTART_CMD)


def deactivate_nodes():
    environment = conftest.environment()
    __execute_command_in_nodes(environment, MYSQL_STOP_CMD)


def __execute_command_in_nodes(environment, command):
    for node in environment.nodes:
        __execute_command_in_node(node, command)


def deactivate_node(node):
    return __execute_command_in_node(node, MYSQL_STOP_CMD)


def activate_node(node):
    return __execute_command_in_node(node, MYSQL_START_CMD)


def __execute_command_in_node(node, command):
    remote = RemoteHostInterface(node.address, node.user, node.password, node.port)
    return remote.exec_remote_command(command)


def is_replication_ok(environment, capsys):
    node = get_node_from_status(environment.master, capsys)
    if node['repl_status'] != 'running':
        return False

    node = get_node_from_status(environment.replication, capsys)
    if node['repl_status'] != 'running':
        return False

    return True


def wait_for_replication_ok(environment, capsys):
    for _ in xrange(12):
        if is_replication_ok(environment, capsys):
            break
        time.sleep(5)
    time.sleep(1)
