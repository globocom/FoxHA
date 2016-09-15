import node_utils
from query import Query
from errors import NoWriteNodeError, NoReadNodeError


class Group(object):

    def __init__(self, name, connection):
        self.name = name
        self.connection = connection

    def __config_from_fox_repository(self):
        return self.connection.execute(Query.SQL_CONFIG_GROUP % self.name)[0]

    @property
    def description(self):
        return self.__config_from_fox_repository()['description']

    @property
    def vip_address(self):
        return self.__config_from_fox_repository()['vip_address']

    @property
    def mysql_adm_user(self):
        return self.__config_from_fox_repository()['mysql_adm_user']

    @property
    def mysql_repl_user(self):
        return self.__config_from_fox_repository()['mysql_repl_user']

    @property
    def nodes(self):
        return node_utils.get_all_nodes(self.name, self.connection)

    @property
    def master_node(self):
        for node in self.nodes:
            if node.is_read_write():
                return node

        raise NoWriteNodeError(self.name)

    @property
    def replication_node(self):
        for node in self.nodes:
            if node.is_read_only():
                return node
        raise NoReadNodeError(self.name)

    def __eq__(self, other):
        return self.name == other.name
