import pytest
from foxha.node import LogicalNode
import foxha.fox
import test_utils


def setup_module(module):
    test_utils.connect_database()


def teardown_module(module):
    test_utils.reset_database()


def setup_function(module):
    test_utils.reset_database()


@pytest.fixture
def logical_replication_node(environment, default_connection):
    return LogicalNode(
        environment.group, environment.replication, 'master',
        default_connection
    )


def test_can_create_node(environment, logical_replication_node):
    assert logical_replication_node.group == environment.group
    assert logical_replication_node.ip == environment.replication
    assert logical_replication_node.name == 'master'
    assert logical_replication_node.address == 'master(%s)' % environment.replication
    assert logical_replication_node.fox_status == 'enabled'
    assert logical_replication_node.fox_mode == 'read_only'


def test_status_enabled(environment, logical_replication_node):
    assert logical_replication_node.fox_status == 'enabled'
    assert logical_replication_node.is_enabled()
    assert not logical_replication_node.is_disabled()
    assert not logical_replication_node.is_failed()


def test_status_disabled(environment, logical_replication_node):
    foxha.fox.set('disabled', environment.group, environment.replication)
    assert logical_replication_node.fox_status == 'disabled'
    assert not logical_replication_node.is_enabled()
    assert logical_replication_node.is_disabled()
    assert not logical_replication_node.is_failed()


def test_status_failed(environment, logical_replication_node):
    foxha.fox.set('failed', environment.group, environment.replication)
    assert logical_replication_node.fox_status == 'failed'
    assert not logical_replication_node.is_enabled()
    assert not logical_replication_node.is_disabled()
    assert logical_replication_node.is_failed()


def test_mode_read_write(environment, logical_replication_node, capsys):
    test_utils.wait_for_replication_ok(environment, capsys)
    foxha.fox.set_read_write(environment.group, environment.replication)
    assert logical_replication_node.fox_mode == 'read_write'
    assert not logical_replication_node.is_fox_mode_read_only()
    assert logical_replication_node.is_fox_mode_read_write()


def test_mode_read_only(environment, logical_replication_node):
    assert logical_replication_node.fox_mode == 'read_only'
    assert not logical_replication_node.is_fox_mode_read_write()
    assert logical_replication_node.is_fox_mode_read_only()
