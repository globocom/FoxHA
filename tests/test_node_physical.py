import time
import pytest
from foxha.node import Node, PhysicalNode
from foxha.utils import Utils
import conftest
import test_utils


@pytest.fixture
def physical_master_node(test_key_path, environment):
    node = Node(
        environment.group, environment.master, conftest.default_connection()
    )

    return PhysicalNode(
        node.ip, node.port, node.mysql_user, node.mysql_password,
        Utils.parse_key_file(test_key_path)
    )


@pytest.fixture
def physical_replication_node(test_key_path, environment):
    node = Node(
        environment.group, environment.replication,
        conftest.default_connection()
    )

    return PhysicalNode(
        node.ip, node.port, node.mysql_user, node.mysql_password,
        Utils.parse_key_file(test_key_path)
    )


def setup_module(module):
    test_utils.connect_database()


def teardown_module(module):
    test_utils.activate_nodes()
    test_utils.reset_database()


def setup_function(module):
    test_utils.activate_nodes()
    test_utils.reset_database()


def test_heartbeat(environment, capsys, physical_replication_node):
    test_utils.wait_for_replication_ok(environment, capsys)
    assert physical_replication_node.seconds_behind == 0


def test_heartbeat_with_delay(environment, physical_replication_node):
    test_utils.deactivate_node(environment.master_node)
    time.sleep(5)
    assert physical_replication_node.seconds_behind > 0


def test_mysql_status_up(environment, physical_master_node):
    assert physical_master_node.mysql_status == 'Up'
    assert physical_master_node.is_mysql_status_up()
    assert not physical_master_node.is_mysql_status_down()


def test_mysql_status_down(environment, physical_master_node):
    test_utils.deactivate_node(environment.master_node)
    assert physical_master_node.mysql_status == 'Down'
    assert not physical_master_node.is_mysql_status_up()
    assert physical_master_node.is_mysql_status_down()


def test_node_master_with_master_down(environment, physical_replication_node):
    test_utils.deactivate_node(environment.master_node)
    time.sleep(5)
    assert physical_replication_node.master


def test_node_mode(physical_master_node, physical_replication_node):
    assert physical_master_node.mode == 'read_write'
    assert physical_master_node.is_read_write()
    assert not physical_master_node.is_read_only()

    assert physical_replication_node.mode == 'read_only'
    assert physical_replication_node.is_read_only()
    assert not physical_replication_node.is_read_write()


def test_replication_status(physical_replication_node):
    assert physical_replication_node.replication_status == 'running'
    assert physical_replication_node.is_replication_running()
    assert not physical_replication_node.is_replication_stopped()


def test_replication_status_with_node_down(environment,
                                           physical_replication_node):
    test_utils.deactivate_node(environment.master_node)
    time.sleep(5)
    assert physical_replication_node.replication_status == 'stopped'
    assert physical_replication_node.is_replication_stopped()
    assert not physical_replication_node.is_replication_running()


def test_server_none_with_node_down(environment, physical_replication_node):
    test_utils.deactivate_node(environment.replication_node)

    assert physical_replication_node.mode == '-'
    assert physical_replication_node.replication_status == '-'
    assert physical_replication_node.seconds_behind == '-'
    assert not physical_replication_node.master
    assert not physical_replication_node.server_id
    assert not physical_replication_node.master_server_id
