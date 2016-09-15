import pytest
from foxha import inner_logic
from foxha.group import Group
from foxha.query import Query
from foxha.node import LogicalNode
from foxha.errors import GroupNotFoundError, NodeNotFoundError, \
    NoWriteNodeError, ManyWriteNodesError, NodeIsDownError, \
    ReplicationNotRunningError, IsNotMasterMasterEnvironmentError
import test_utils


def setup_module(module):
    test_utils.connect_database()


def teardown_module(module):
    test_utils.reset_database()


def setup_function(module):
    test_utils.reset_database()


def test_can_list_all_groups(environment, default_connection):
    groups = inner_logic.get_groups(default_connection)
    assert Group(environment.group, default_connection) in groups


def test_cannot_found_external_group_in_list(default_connection):
    groups = inner_logic.get_groups(default_connection)
    assert Group('Strange_Group_Env', default_connection) not in groups


def test_can_find_nodes_in_list(environment, default_connection):
    node_list = inner_logic.get_nodes(environment.group, default_connection)
    env_nodes = environment.nodes
    assert len(env_nodes) == len(node_list)

    for node in env_nodes:
        assert LogicalNode(
            environment.group, node.address, '', default_connection
        ) in node_list


def test_cannot_found_node_for_external_group(environment, default_connection):
    node_list = inner_logic.get_nodes('Strange_Group_Env', default_connection)
    assert len(node_list) == 0


def test_can_get_group(environment, default_connection):
    group = inner_logic.get_group(environment.group, default_connection)
    assert Group(environment.group, default_connection) == group


def test_cannot_get_group_external(environment, default_connection):
    with pytest.raises(GroupNotFoundError):
        inner_logic.get_group('Strange_Group_Env', default_connection)


def test_can_get_node(environment, default_connection):
    node = inner_logic.get_node(
        environment.group, environment.master, default_connection
    )
    assert node.ip == environment.master
    assert node.group == environment.group


def test_cannot_get_node(environment, default_connection):
    with pytest.raises(NodeNotFoundError):
        inner_logic.get_node(
            'Strange_Group_Env', '111.222.333.444', default_connection
        )


def test_cannot_get_node_wrong_group(environment, default_connection):
    with pytest.raises(NodeNotFoundError):
        inner_logic.get_node(
            'Strange_Group_Env', environment.master, default_connection
        )


def test_cannot_get_node_wrong_ip(environment, default_connection):
    with pytest.raises(NodeNotFoundError):
        inner_logic.get_node(
            environment.group, '111.222.333.444', default_connection
        )


def test_can_start_group(environment, default_connection):
    node_write = inner_logic.get_node(
        environment.group, environment.master, default_connection
    )
    node_write.node_connection.query(Query.SET_MODE % 'ON')
    assert node_write.mode != node_write.fox_mode

    assert inner_logic.start(environment.group, default_connection)
    assert node_write.mode == node_write.fox_mode


def test_cannot_start_group_without_write(environment, default_connection):
    node_write = inner_logic.get_node(
        environment.group, environment.master, default_connection
    )
    node_write.fox_connection.query(
        Query.UPDATE_MODE % ('read_only', node_write.ip, node_write.group)
    )
    assert node_write.mode != node_write.fox_mode

    with pytest.raises(NoWriteNodeError):
        inner_logic.start(environment.group, default_connection)


def test_cannot_start_group_with_many_write(environment, default_connection):
    node_repl = inner_logic.get_node(
        environment.group, environment.replication, default_connection
    )
    node_repl.fox_connection.query(
        Query.UPDATE_MODE % ('read_write', node_repl.ip, node_repl.group)
    )
    assert node_repl.mode != node_repl.fox_mode

    with pytest.raises(ManyWriteNodesError):
        inner_logic.start(environment.group, default_connection)

    node_repl.fox_connection.query(
        Query.UPDATE_MODE % ('read_only', node_repl.ip, node_repl.group)
    )
    assert node_repl.mode == node_repl.fox_mode


def test_cannot_start_with_master_node_down(environment, default_connection):
    node_write = inner_logic.get_node(
        environment.group, environment.master, default_connection
    )
    assert node_write.is_mysql_status_up()

    test_utils.deactivate_node(environment.master_node)
    assert node_write.is_mysql_status_down()
    with pytest.raises(NodeIsDownError):
        inner_logic.start(environment.group, default_connection)

    test_utils.activate_node(environment.master_node)


def test_cannot_set_write_without_replication(
        environment, default_connection, capsys
):
    test_utils.wait_for_replication_ok(environment, capsys)
    node_replication = inner_logic.get_node(
        environment.group, environment.replication, default_connection
    )
    assert node_replication.is_replication_running()

    node_replication.node_connection.query(Query.SQL_STOP_SLAVE)
    assert node_replication.is_replication_stopped()

    try:
        inner_logic.set_read_write(node_replication, default_connection)
    except ReplicationNotRunningError:
        assert True
    else:
        assert False, 'DO NOT RAISE ReplicationNotRunningError'
    finally:
        node_replication.node_connection.query(Query.SQL_START_SLAVE)
        test_utils.wait_for_replication_ok(environment, capsys)
        assert node_replication.is_replication_running()


def test_cannot_switch_with_no_master_master(environment, default_connection):
    inner_logic.add_node(
        default_connection, environment.group, 'FakeNode',
        '127.0.0.1', 3306, 'read_only', 'enabled'
    )

    try:
        inner_logic.switchover(environment.group, default_connection)
        assert False
    except IsNotMasterMasterEnvironmentError:
        assert True
    except:
        assert False
    finally:
        inner_logic.delete_node(
            default_connection, environment.group, '127.0.0.1'
        )


def test_cannot_failover_with_no_master_master(environment, default_connection):
    inner_logic.add_node(
        default_connection, environment.group, 'FakeNode',
        '127.0.0.1', 3306, 'read_only', 'enabled'
    )

    try:
        inner_logic.failover(environment.group, default_connection)
        assert False
    except IsNotMasterMasterEnvironmentError:
        assert True
    except:
        assert False
    finally:
        inner_logic.delete_node(
            default_connection, environment.group, '127.0.0.1'
        )


def test_cannot_failover_node_down(environment, default_connection, capsys):
    test_utils.deactivate_node(environment.replication_node)

    try:
        inner_logic.failover(environment.group, default_connection)
        assert False
    except NodeIsDownError:
        assert True
    except:
        assert False
    finally:
        test_utils.activate_node(environment.replication_node)
        test_utils.wait_for_replication_ok(environment, capsys)
