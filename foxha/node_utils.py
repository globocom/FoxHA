from query import Query
from node import Node


def _get_nodes_by_query(query, group, connection):
    result = connection.execute(query % group)
    return [Node(group, node['node_ip'], connection)
            for node in result]


def get_all_nodes(group, connection):
    return _get_nodes_by_query(Query.SQL_LIST_NODES, group, connection)


def get_enabled_nodes(group, connection):
    return _get_nodes_by_query(Query.SQL_LIST_NODES_ENABLED, group, connection)
