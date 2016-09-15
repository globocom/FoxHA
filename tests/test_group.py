import pytest
from foxha.group import Group
import foxha.fox
import test_utils
from foxha.errors import NoWriteNodeError, NoReadNodeError


def setup_module(module):
    test_utils.connect_database()


def teardown_module(module):
    test_utils.reset_database()


def setup_function(module):
    test_utils.reset_database()


@pytest.fixture
def main_group(environment, default_connection):
    return Group(environment.group, default_connection)


def test_can_create_group(environment, main_group):
    assert main_group.name == environment.group
    assert main_group.description == environment.description
    assert main_group.vip_address == environment.vip_address
    assert main_group.mysql_adm_user == environment.mysql_adm_user
    assert main_group.mysql_repl_user == environment.mysql_repl_user
    assert len(main_group.nodes) == len(environment.nodes)
    assert main_group.master_node.ip == environment.master
    assert main_group.replication_node.ip == environment.replication


def test_no_master_node(environment, main_group):
    foxha.fox.set_read_only(environment.group, environment.master)
    with pytest.raises(NoWriteNodeError):
        assert environment.master == main_group.master_node.ip


def test_no_replication_node(environment, main_group):
    foxha.fox.set('failed', environment.group, environment.master)
    foxha.fox.set_read_write(environment.group, environment.replication)
    with pytest.raises(NoReadNodeError):
        assert environment.replication == main_group.replication_node.ip
