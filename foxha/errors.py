
class ManyWriteNodesError(EnvironmentError):
    def __init__(self, group, nodes):
        msg = 'The group "{}" has {} write nodes. Should be just one'\
            .format(group, nodes)
        super(EnvironmentError, self).__init__(msg)


class NoWriteNodeError(EnvironmentError):
    def __init__(self, group):
        msg = 'The group "{}" don\'t have write node'.format(group)
        super(EnvironmentError, self).__init__(msg)


class NoReadNodeError(EnvironmentError):
    def __init__(self, group):
        msg = 'The group "{}" don\'t have read node'.format(group)
        super(EnvironmentError, self).__init__(msg)


class IsNotMasterMasterEnvironmentError(EnvironmentError):
    def __init__(self, group):
        msg = 'The group "{}" don\'t have read node'.format(group)
        super(EnvironmentError, self).__init__(msg)


class NodeIsDownError(EnvironmentError):
    def __init__(self, node):
        msg = 'Could not connect with node "{}"'.format(node)
        super(EnvironmentError, self).__init__(msg)


class ReplicationNotRunningError(EnvironmentError):
    def __init__(self, node):
        msg = 'The replication is stopped at node "{}"'.format(node)
        super(EnvironmentError, self).__init__(msg)


class NodeWithDelayError(EnvironmentError):
    def __init__(self, node, delay):
        msg = 'The node "{}" is {} seconds delayed'.format(node, delay)
        super(EnvironmentError, self).__init__(msg)


class GroupNotFoundError(EnvironmentError):
    def __init__(self, group):
        msg = 'Group "{}" not found'.format(group)
        super(EnvironmentError, self).__init__(msg)


class NodeNotFoundError(EnvironmentError):
    def __init__(self, node, group):
        msg = 'Node "{}" not found in group "{}"'.format(node, group)
        super(EnvironmentError, self).__init__(msg)


class GroupAlreadyAddedError(EnvironmentError):
    def __init__(self, group):
        msg = 'Group "{}" already added'.format(group)
        super(EnvironmentError, self).__init__(msg)


class NodeAlreadyAddedError(EnvironmentError):
    def __init__(self, node, group):
        msg = 'Node "{}" already added in group "{}"'.format(node, group)
        super(EnvironmentError, self).__init__(msg)


class GroupWithNodesError(EnvironmentError):
    def __init__(self, group, nodes):
        msg = 'The group "{}" has "{}" nodes'.format(group, nodes)
        super(EnvironmentError, self).__init__(msg)
