from time import sleep
from foxha import fox
import test_utils


def setup_module(module):
    test_utils.connect_database()


def teardown_module(module):
    test_utils.reset_database()


def setup_function(module):
    test_utils.reset_database()


def test_can_switch_between_nodes(environment, capsys):
    test_utils.wait_for_replication_ok(environment, capsys)

    fox.switchover(environment.group)
    sleep(15)

    node = test_utils.get_node_from_status(environment.master, capsys)
    assert node['mode'] == 'read_only'
    node = test_utils.get_node_from_status(environment.replication, capsys)
    assert node['mode'] == 'read_write'


def test_cannot_switch_with_no_write_node(environment, capsys):
    node = test_utils.set_read_only(environment.master, capsys)
    assert node['mode'] == 'read_only'

    fox.switchover(environment.group)

    node = test_utils.get_node_from_list(environment.master, capsys)
    assert node['status'] == 'enabled'
    node = test_utils.get_node_from_status(environment.replication, capsys)
    assert node['mode'] == 'read_only'


def test_switchover_twice(environment, capsys):
    test_utils.wait_for_replication_ok(environment, capsys)

    fox.switchover(environment.group)
    node = test_utils.get_node_from_status(environment.master, capsys)
    assert node['mode'] == 'read_only'
    node = test_utils.get_node_from_status(environment.replication, capsys)
    assert node['mode'] == 'read_write'

    fox.switchover(environment.group)

    node = test_utils.get_node_from_status(environment.master, capsys)
    assert node['mode'] == 'read_write'
    node = test_utils.get_node_from_status(environment.replication, capsys)
    assert node['mode'] == 'read_only'
