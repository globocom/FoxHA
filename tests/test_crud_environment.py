import pytest
from foxha import inner_logic
from foxha.query import Query
from foxha.errors import GroupNotFoundError, GroupAlreadyAddedError, \
    NodeAlreadyAddedError, NodeNotFoundError, GroupWithNodesError
import conftest


def clear_database():
    group = GroupEnv()
    node = NodeEnv()
    connection = conftest.default_connection()
    connection.query(Query.SQL_DELETE_NODE.format(node.group, node.ip))
    connection.query(Query.SQL_DELETE_GROUP.format(group.name))


def teardown_module(module):
    clear_database()


def setup_function(module):
    clear_database()


class GroupEnv(object):
    def __init__(self):
        self.name = 'test_env'
        self.description = 'Fake env'
        self.vip_address = 'vip.off.com'
        self.mysql_user = 'one'
        self.mysql_pass = 'two'
        self.relp_user = 'three'
        self.relp_pass = 'four'


@pytest.fixture
def group():
    return GroupEnv()


class NodeEnv(object):
    def __init__(self):
        self.group = 'test_env'
        self.name = 'fake'
        self.ip = '127.0.0.1'
        self.port = 3306
        self.mode = 'read_write'
        self.status = 'enabled'


@pytest.fixture
def node():
    return NodeEnv()


def test_can_add_new_group(default_connection, group):
    inner_logic.add_group(
        default_connection, group.name, group.description, group.vip_address,
        group.mysql_user, group.mysql_pass, group.relp_user, group.relp_pass
    )

    assert inner_logic.get_added_group(
        group.name, default_connection
    ).name == group.name


def test_cannot_add_added_group(default_connection, group):
    inner_logic.add_group(
        default_connection, group.name, group.description, group.vip_address,
        group.mysql_user, group.mysql_pass, group.relp_user, group.relp_pass
    )

    with pytest.raises(GroupAlreadyAddedError):
        inner_logic.add_group(
            default_connection, group.name, group.description,
            group.vip_address, group.mysql_user, group.mysql_pass,
            group.relp_user, group.relp_pass
        )


def test_can_delete_added_group(default_connection, group):
    inner_logic.add_group(
        default_connection, group.name, group.description, group.vip_address,
        group.mysql_user, group.mysql_pass, group.relp_user, group.relp_pass
    )
    assert inner_logic.delete_group(default_connection, group.name)

    with pytest.raises(GroupNotFoundError):
        inner_logic.get_group(group.name, default_connection)


def test_cannot_delete_external_group(default_connection, group):
    with pytest.raises(GroupNotFoundError):
        inner_logic.delete_group(default_connection, group.name)


def test_cannot_delete_group_with_nodes(default_connection, group, node):
    inner_logic.add_group(
        default_connection, group.name, group.description, group.vip_address,
        group.mysql_user, group.mysql_pass, group.relp_user, group.relp_pass
    )
    inner_logic.add_node(
        default_connection, node.group, node.name,
        node.ip, node.port, node.mode, node.status
    )

    with pytest.raises(GroupWithNodesError):
        inner_logic.delete_group(default_connection, group.name)


def test_can_add_node(default_connection, node, group):
    inner_logic.add_group(
        default_connection, group.name, group.description, group.vip_address,
        group.mysql_user, group.mysql_pass, group.relp_user, group.relp_pass
    )

    inner_logic.add_node(
        default_connection, node.group, node.name,
        node.ip, node.port, node.mode, node.status
    )

    added_node = inner_logic.get_node(node.group, node.ip, default_connection)
    assert added_node.group == node.group
    assert added_node.ip == node.ip
    assert added_node.name == node.name


def test_cannot_add_added_node(default_connection, node, group):
    inner_logic.add_group(
        default_connection, group.name, group.description, group.vip_address,
        group.mysql_user, group.mysql_pass, group.relp_user, group.relp_pass
    )

    inner_logic.add_node(
        default_connection, node.group, node.name,
        node.ip, node.port, node.mode, node.status
    )

    with pytest.raises(NodeAlreadyAddedError):
        inner_logic.add_node(
            default_connection, node.group, node.name,
            node.ip, node.port, node.mode, node.status
        )


def test_cannot_add_node_external_group(default_connection, node):
    with pytest.raises(GroupNotFoundError):
        inner_logic.add_node(
            default_connection, node.group, node.name,
            node.ip, node.port, node.mode, node.status
        )


def test_can_delete_added_node(default_connection, node, group):
    inner_logic.add_group(
        default_connection, group.name, group.description, group.vip_address,
        group.mysql_user, group.mysql_pass, group.relp_user, group.relp_pass
    )

    inner_logic.add_node(
        default_connection, node.group, node.name,
        node.ip, node.port, node.mode, node.status
    )
    inner_logic.delete_node(default_connection, node.group, node.ip)

    with pytest.raises(NodeNotFoundError):
        inner_logic.get_node(node.group, node.ip, default_connection)


def test_cannot_delete_external_node(default_connection, node):
    with pytest.raises(NodeNotFoundError):
        inner_logic.delete_node(default_connection, node.group, node.ip)


def test_not_master_master_with_one_node(default_connection, group, node):
    inner_logic.add_group(
        default_connection, group.name, group.description, group.vip_address,
        group.mysql_user, group.mysql_pass, group.relp_user, group.relp_pass
    )
    inner_logic.add_node(
        default_connection, node.group, node.name,
        node.ip, node.port, node.mode, node.status
    )
    assert not inner_logic.is_master_master(group.name, default_connection)


def test_not_master_master_with_more_than_two_nodes(
        default_connection, group, node
):
    inner_logic.add_group(
        default_connection, group.name, group.description, group.vip_address,
        group.mysql_user, group.mysql_pass, group.relp_user, group.relp_pass
    )
    inner_logic.add_node(
        default_connection, node.group, node.name,
        node.ip, node.port, node.mode, node.status
    )
    inner_logic.add_node(
        default_connection, node.group, 'Fake-2',
        '127.0.0.2', node.port, node.mode, node.status
    )
    inner_logic.add_node(
        default_connection, node.group, 'Fake-3',
        '127.0.0.3', node.port, node.mode, node.status
    )

    is_master_master = inner_logic.is_master_master(
        group.name, default_connection
    )
    assert inner_logic.delete_node(default_connection, node.group, '127.0.0.2')
    assert inner_logic.delete_node(default_connection, node.group, '127.0.0.3')
    assert not is_master_master
