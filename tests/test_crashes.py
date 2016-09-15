import time
import pytest
from foxha import fox
from foxha import inner_logic
from foxha.errors import NodeIsDownError
import test_utils


def setup_module(module):
    test_utils.connect_database()


def teardown_module(module):
    test_utils.activate_nodes()
    test_utils.reset_database()
    time.sleep(30)


def setup_function(module):
    test_utils.activate_nodes()
    test_utils.reset_database()


def shut_down_master_node(environment):
    code, out, err = test_utils.deactivate_node(environment.master_node)
    assert code == 0


def start_up_master_node(environment):
    code, out, err = test_utils.activate_node(environment.master_node)
    assert code == 0


def test_cannot_change_to_write_when_replication_is_off(environment, capsys):
    node = test_utils.get_node_from_status(environment.replication, capsys)
    assert node['mode'] == 'read_only'

    shut_down_master_node(environment)
    node = test_utils.set_read_only(environment.replication, capsys)
    assert node['mode'] == 'read_only'


def test_cannot_change_to_read_when_node_is_down(environment, capsys):
    shut_down_master_node(environment)
    fox.set_read_only(environment.group, environment.master)

    message = '-set read_only failed. Connection could not be established ' \
              'with the node_ip %s' % environment.master
    out, err = capsys.readouterr()
    assert message in out


def test_can_failover_with_node_write_down(environment, capsys):
    shut_down_master_node(environment)
    fox.failover(environment.group)

    node = test_utils.get_node_from_status(environment.replication, capsys)
    assert node['mode'] == 'read_write'


def test_status_is_down_after_crash(environment, capsys):
    node = test_utils.get_node_from_status(environment.master, capsys)
    assert node['status'] == 'Up'

    shut_down_master_node(environment)
    node = test_utils.get_node_from_status(environment.master, capsys)
    assert node['status'] == 'Down'


def test_can_change_down_note_to_failed(environment, capsys):
    shut_down_master_node(environment)

    node = test_utils.failed_node(environment.master, capsys)
    assert node['status'] == 'failed'


def test_status_after_restart(environment, capsys):
    shut_down_master_node(environment)
    node = test_utils.get_node_from_status(environment.master, capsys)
    assert node['status'] == 'Down'

    start_up_master_node(environment)
    node = test_utils.get_node_from_status(environment.master, capsys)
    assert node['status'] == 'Up'


def test_can_change_status_to_enabled_after_restart(environment, capsys):
    shut_down_master_node(environment)
    node = test_utils.failed_node(environment.master, capsys)
    assert node['status'] == 'failed'
    start_up_master_node(environment)

    node = test_utils.enable_node(environment.master, capsys)
    assert node['status'] == 'enabled'


def test_cannot_set_write_to_down_node(environment, default_connection):
    node = inner_logic.get_node(
        environment.group, environment.master, default_connection
    )
    shut_down_master_node(environment)

    with pytest.raises(NodeIsDownError):
        inner_logic.set_read_write(node, default_connection)


def test_no_master_master_with_down_node(environment, default_connection):
    shut_down_master_node(environment)

    assert not inner_logic.is_master_master(
        environment.group, default_connection
    )
