import time
import re
import pytest
from foxha import fox
import test_utils


def setup_module(module):
    test_utils.connect_database()


def teardown_module(module):
    test_utils.reset_database()


def setup_function(module):
    test_utils.reset_database()


def test_can_change_node_to_read_only(environment, capsys):
    node = test_utils.set_read_only(environment.master, capsys)
    assert node['mode'] == 'read_only'


def test_cannot_change_to_read_when_already_is_read(environment, capsys):
    node = test_utils.set_read_only(environment.replication, capsys)
    assert node['mode'] == 'read_only'


def test_can_change_node_to_read_write(environment, capsys):
    node = test_utils.set_read_only(environment.master, capsys)
    assert node['mode'] == 'read_only'

    node = test_utils.set_read_write(environment.replication, capsys)
    assert node['mode'] == 'read_write'


@pytest.mark.flaky(reruns=5)
def test_cannot_change_to_write_with_heartbeat_delay(environment, capsys):
    node = test_utils.set_read_only(environment.master, capsys)
    assert node['mode'] == 'read_only'

    time.sleep(2)

    node = test_utils.set_read_write(environment.master, capsys)
    assert node['mode'] == 'read_write'

    fox.set('read_write', environment.group, environment.replication)
    delay_message = 'The node "%s" is (\d+.\d+) seconds delayed and ' \
                    'cannot be set as read_write.' % environment.replication
    out, err = capsys.readouterr()
    assert re.findall(delay_message, out)

    node = test_utils.get_node_from_status(environment.replication, capsys)
    assert node['mode'] == 'read_only'


def test_cannot_change_to_write_when_already_is_write(environment, capsys):
    node = test_utils.set_read_write(environment.master, capsys)
    assert node['mode'] == 'read_write'


def test_can_enable_node(environment, capsys):
    node = test_utils.disable_node(environment.replication, capsys)
    assert node['status'] == 'disabled'

    node = test_utils.enable_node(environment.replication, capsys)
    assert node['status'] == 'enabled'


def test_can_disable_node_without_write(environment, capsys):
    node = test_utils.set_read_only(environment.master, capsys)
    assert node['mode'] == 'read_only'

    node = test_utils.disable_node(environment.master, capsys)
    assert node['status'] == 'disabled'

    node = test_utils.disable_node(environment.replication, capsys)
    assert node['status'] == 'disabled'


def test_cannot_disable_write_node(environment, capsys):
    node = test_utils.get_node_from_status(environment.master, capsys)
    assert node['mode'] == 'read_write'

    node = test_utils.disable_node(environment.master, capsys)
    assert node['status'] == 'enabled'


def test_can_disable_read_node(environment, capsys):
    node = test_utils.disable_node(environment.replication, capsys)
    assert node['status'] == 'disabled'


def test_can_fail_without_write(environment, capsys):
    node = test_utils.set_read_only(environment.master, capsys)
    assert node['mode'] == 'read_only'

    node = test_utils.failed_node(environment.master, capsys)
    assert node['status'] == 'failed'

    node = test_utils.failed_node(environment.replication, capsys)
    assert node['status'] == 'failed'


def test_can_fail_read_node(environment, capsys):
    node = test_utils.failed_node(environment.replication, capsys)
    assert node['status'] == 'failed'


def test_failover_when_write_node_failed(environment, capsys):
    node = test_utils.failed_node(environment.master, capsys)
    assert node['status'] == 'failed'

    node = test_utils.get_node_from_list(environment.replication, capsys)
    assert node['status'] == 'enabled'
    node = test_utils.get_node_from_status(environment.replication, capsys)
    assert node['mode'] == 'read_write'
