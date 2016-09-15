from query import Query
from group import Group
from node import Node
import node_utils
from errors import ManyWriteNodesError, NoWriteNodeError, NodeIsDownError,\
    IsNotMasterMasterEnvironmentError, ReplicationNotRunningError, \
    NodeWithDelayError, GroupNotFoundError, NodeNotFoundError, \
    GroupAlreadyAddedError, NodeAlreadyAddedError, GroupWithNodesError


def get_nodes(group, connection):
    return node_utils.get_all_nodes(group, connection)


def get_groups(connection):
    result = connection.execute(Query.SQL_LIST)
    return [Group(group['group_name'], connection) for group in result]


def get_write_node(group, connection):
    result = connection.execute(Query.SQL_CHECK_WRITE % group)

    if len(result) == 1:
        return Node(group, result[0]['node_ip'], connection)
    elif len(result) > 1:
        raise ManyWriteNodesError(group, len(result))
    else:
        raise NoWriteNodeError(group)


def is_master_master(group, connection):
    result = connection.execute(Query.SQL_REPO % group)
    if len(result) != 2:
        return False

    nodes = get_nodes(group, connection)
    master = nodes[0]
    pair = nodes[1]
    if master.is_replication_running() and pair.is_replication_running():
        same_server = master.server_id == pair.master_server_id
        same_replication = master.master_server_id == pair.server_id
        return same_server and same_replication

    return False


def set_read_write(node, connection):
    if node.is_mysql_status_down():
        raise NodeIsDownError(node.ip)

    try:
        node_write = get_write_node(node.group, connection)
    except NoWriteNodeError:
        node.node_connection.execute(Query.SET_MODE % 'OFF')
        connection.query(
            Query.UPDATE_MODE % ('read_write', node.ip, node.group)
        )
        return True

    if node == node_write:
        node.node_connection.query(Query.SET_MODE % 'OFF')
        return True

    if node.is_replication_stopped():
        raise ReplicationNotRunningError(node.ip)

    if node.seconds_behind > 0:
        raise NodeWithDelayError(node.ip, node.seconds_behind)

    set_read_only(node_write, connection)
    node.node_connection.execute(Query.SET_MODE % 'OFF')
    connection.query(Query.UPDATE_MODE % ('read_write', node.ip, node.group))
    return True


def set_read_only(node, connection):
    if node.is_mysql_status_down():
        raise NodeIsDownError(node.ip)

    node.node_connection.query(Query.SET_MODE % 'ON')
    connection.query(Query.UPDATE_MODE % ('read_only', node.ip, node.group))
    return True


def switchover(group, connection):
    get_write_node(group, connection)

    if not is_master_master(group, connection):
        raise IsNotMasterMasterEnvironmentError(group)

    for node in get_nodes(group, connection):
        if not node.is_read_write():
            if set_read_write(node, connection):
                break

    return True


def failover(group, connection):
    node_write = get_write_node(group, connection)

    nodes = get_nodes(group, connection)

    if len(nodes) != 2:
        raise IsNotMasterMasterEnvironmentError(group)

    connection.query(Query.UPDATE_STATE % ('failed', node_write.ip, group))
    connection.query(Query.UPDATE_MODE % ('read_only', node_write.ip, group))

    for node in nodes:
        if node.is_enabled():
            if node.is_mysql_status_down():
                raise NodeIsDownError(node.ip)

            connection.query(
                Query.UPDATE_MODE % ('read_write', node.ip, group)
            )
            node.node_connection.query(Query.SET_MODE % 'OFF')
            return True
    return False


def get_group(name, connection):
    result = connection.execute(Query.SQL_GROUP_EXIST % name)

    if len(result) == 0:
        raise GroupNotFoundError(name)

    return Group(result[0]['group_name'], connection)


def get_added_group(name, connection):
    result = connection.execute(Query.SQL_GROUP_ADDED % name)
    if len(result) > 0:
        return Group(result[0]['group_name'], connection)


def get_node(group, node_ip, connection):
    result = connection.execute(Query.SQL_NODE_EXIST % (group, node_ip))

    if len(result) == 0:
        raise NodeNotFoundError(node_ip, group)

    return Node(group, node_ip, connection)


def add_group(
        connection, group_name, description, vip_address,
        mysql_user, mysql_password, repl_user, repl_password):

    if get_added_group(group_name, connection):
        raise GroupAlreadyAddedError(group_name)

    connection.query(
        Query.SQL_INSERT_GROUP.format(
            group_name, description, vip_address,
            mysql_user, connection.cipher.encrypt(mysql_password),
            repl_user, connection.cipher.encrypt(repl_password)
        )
    )
    return True


def delete_group(connection, group_name):
    group = get_added_group(group_name, connection)
    if not group:
        raise GroupNotFoundError(group_name)

    if len(group.nodes) > 0:
        raise GroupWithNodesError(group_name, len(group.nodes))

    connection.query(Query.SQL_DELETE_GROUP.format(group_name))
    return True


def add_node(connection, group_name, name, ip, port, mode, status):
    if not get_added_group(group_name, connection):
        raise GroupNotFoundError(group_name)

    try:
        get_node(group_name, ip, connection)
        raise NodeAlreadyAddedError(ip, group_name)
    except NodeNotFoundError:
        pass

    connection.query(
        Query.SQL_INSERT_NODE.format(group_name, name, ip, port, mode, status)
    )
    return True


def delete_node(connection, group_name, node_ip):
    get_node(group_name, node_ip, connection)
    connection.query(Query.SQL_DELETE_NODE.format(group_name, node_ip))
    return True


def start(group_name, connection):
    node_write = get_write_node(group_name, connection)

    if node_write.is_mysql_status_down():
        raise NodeIsDownError(node_write.ip)

    node_write.node_connection.query(Query.SET_MODE % 'OFF')
    return True
