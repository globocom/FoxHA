from query import Query
from node import Node


def get_all_nodes(group, connection):
    result = connection.execute(Query.SQL_LIST_NODES % group)
    return [Node(group, node['node_ip'], connection)
            for node in result]
