from foxha import fox
import test_utils


def setup_module(module):
    test_utils.connect_database()


def teardown_module(module):
    test_utils.reset_database()


def setup_function(module):
    test_utils.reset_database()


def test_can_failover_node(environment, capsys):
    test_utils.wait_for_replication_ok(environment, capsys)

    fox.failover(environment.group)

    node = test_utils.get_node_from_list(environment.master, capsys)
    assert node['status'] == 'failed'
    node = test_utils.get_node_from_status(environment.replication, capsys)
    assert node['mode'] == 'read_write'


def test_cannot_failover_with_no_write_node(environment, capsys):
    test_utils.wait_for_replication_ok(environment, capsys)
    node = test_utils.set_read_only(environment.master, capsys)
    assert node['mode'] == 'read_only'

    fox.failover(environment.group)

    node = test_utils.get_node_from_list(environment.master, capsys)
    assert node['status'] == 'enabled'
    node = test_utils.get_node_from_status(environment.replication, capsys)
    assert node['mode'] == 'read_only'


def test_cannot_failover_no_enabled_node(environment, capsys):
    test_utils.wait_for_replication_ok(environment, capsys)
    node = test_utils.disable_node(environment.replication, capsys)
    assert node['status'] == 'disabled'

    assert not fox.failover(environment.group)

    node = test_utils.enable_node(environment.replication, capsys)
    assert node['status'] == 'enabled'
