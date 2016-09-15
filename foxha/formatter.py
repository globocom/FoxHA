from prettytable import PrettyTable
from print_format import fore_red, fore_green, print_error, print_warning

import inner_logic
from errors import ManyWriteNodesError, NoWriteNodeError, NodeIsDownError,\
    ReplicationNotRunningError, NodeWithDelayError, GroupNotFoundError,\
    IsNotMasterMasterEnvironmentError, NodeNotFoundError

from node import Node


def list_group(connection):
    for group in inner_logic.get_groups(connection):
        print "* {}".format(group.name)
    exit(0)


def list_nodes(group, connection):
    list_table = PrettyTable(["Group_name", "Node", "Status"])
    list_table.header_style = "upper"

    for node in inner_logic.get_nodes(group, connection):
        status = fore_red(node.fox_status)
        if node.is_enabled():
            status = fore_green(node.fox_status)
        list_table.add_row([group, node.address, status])

    print list_table
    exit(0)


def status_nodes(group, logger, connection):
    status_table = PrettyTable(
        ["Group_name",
         "Node",
         "Node_Status",
         "Mode",
         "Repl_Status",
         "Sec_Behind",
         "Master_Host"]
    )
    status_table.header_style = "upper"
    status_table.align = "c"  # Center align

    logger.info('Health of group_name: "{}"'.format(group))

    messages = []
    for node in inner_logic.get_nodes(group, connection):
        if node.is_failed():
            messages.append({
                'text': "Critical -> Node: {} has failed status at "
                        "repository.".format(node.address),
                'Err_Type': 'Critical'})
            logger.critical(
                "{} has failed status at repository.".format(node.address)
            )

        if node.is_mysql_status_up():

            if node.seconds_behind > 0:
                messages.append({
                    'text':
                        "Warning -> Node: {} - Heartbeat is delayed {} "
                        "seconds.".format(
                            node.get_name_ip_port(), str(node.seconds_behind)
                        ),
                    'Err_Type': "Warning"})
                logger.warning(
                    "Node: {} - Heartbeat is delayed {} seconds.".format(
                        node.get_name_ip_port(), node.seconds_behind
                    )
                )

            if node.is_replication_running():
                status_table.add_row([node.group,
                                      node.address,
                                      node.mysql_status,
                                      node.mode,
                                      node.replication_status,
                                      node.seconds_behind,
                                      node.master])
                logger.info(
                    "Node: {}, Mode: {}, Node_status: {}, Replication running,"
                    " Seconds_Behind: {}, Master_Host: {}".format(
                        node.address, node.mode, node.mysql_status,
                        node.seconds_behind, node.master
                    )
                )
            else:
                status_table.add_row([node.group,
                                      node.address,
                                      node.mysql_status,
                                      node.mode,
                                      fore_red(node.replication_status),
                                      " - ",
                                      " - "])
                logger.critical(
                    "Node: {}, Mode: {}, Node_status: {}, "
                    "Replication stopped".format(
                        node.address, node.mode, node.mysql_status
                    )
                )

            if node.mode != node.fox_mode:
                messages.append({
                    'text':
                        'Critical -> Node: {} - Database mode differs '
                        'from repository! Should be {} but is {}.'.format(
                            node.get_name_ip_port(), node.fox_mode, node.mode
                        ),
                    'Err_Type': 'Critical'
                })
                logger.critical(
                    'Database mode on node {} differs from repository! '
                    'Should be {} but is {}.'.format(
                        node.get_name_ip_port(), node.fox_mode, node.mode
                    )
                )
        else:
            status_table.add_row([node.group,
                                  node.address,
                                  fore_red(node.mysql_status, True),
                                  node.fox_mode, '-', '-', '-'])
            messages.append({
                'text': 'Critical -> Node: {} - {}'.format(
                    node.get_name_ip_port(), fore_red(node.mysql_status, True)
                ),
                'Err_Type': "Critical"
            })
            logger.error(
                "Node: {}, Mode: {}, Node_status: {}".format(
                    node.get_name_ip_port(), node.fox_mode, node.mysql_status
                )
            )

    print status_table
    messages.sort(reverse=True)
    for message in messages:
        if message['Err_Type'] == "Critical":
            print_error("{text}".format(**message))
        else:
            print_warning("{text}".format(**message))


def check_write(group, connection, logger):
    try:
        return inner_logic.get_write_node(group, connection)
    except ManyWriteNodesError:
        print_error("Something is wrong! You could not have more than one "
                    "node with read_write mode. Check your configuration!")
        logger.critical(
            "Something is wrong! You could not have more than one node with "
            "read_write mode. Check your configuration!")
        exit(99)
    except NoWriteNodeError:
        logger.info("There isn't any node with the 'read_write' "
                    "mode at group_name: '{}'.".format(group))
    return False


def is_master_master(group, connection, logger):
    if inner_logic.is_master_master(group, connection):
        return True
    else:
        logger.info(
            'Cannot guarantee that replication is '
            'master<->master for group_name: '.format(group)
        )
    return False


def set_read_write(group, node_ip, connection, logger):
    node = Node(group, node_ip, connection)

    try:
        if inner_logic.set_read_write(node, connection):
            logger.info(
                'Node: "{}" defined as "read_write" '
                'at group_name: "{}".'.format(node.ip, node.group)
            )
            return True
    except NodeIsDownError:
        print_error(
            '--set read_write failed. Connection could not '
            'established with the node_ip {}'.format(node_ip)
        )
        logger.error(
            '--set read_write failed. Connection could not '
            'established with the node_ip {}'.format(node_ip)
        )
    except ReplicationNotRunningError:
        print_warning(
            'The replication is stopped at node "{}" and '
            'cannot be set as read_write.'.format(node_ip)
        )
        logger.error(
            'The replication is stopped at node "{}" and '
            'cannot be set as read_write.'.format(node_ip)
        )
    except NodeWithDelayError:
        print_warning(
            'The node "{}" is {} seconds delayed and cannot be set as '
            'read_write.'.format(node_ip, node.seconds_behind)
        )
        logger.error(
            'The node "{}" is {} seconds delayed and cannot be set as '
            'read_write.'.format(node_ip, node.seconds_behind)
        )
    return False


def set_read_only(group, node_ip, connection, logger):
    node = Node(group, node_ip, connection)

    try:
        if inner_logic.set_read_only(node, connection):
            logger.info(
                'Node: "{}" defined as "read_only" '
                'at group_name: "{}"'.format(node.ip, node.group)
            )
            return True
    except NodeIsDownError:
        print_error(
            '--set read_only failed. Connection could not be '
            'established with the node_ip {}'.format(node_ip)
        )
        logger.error(
            '--set read_only failed. Connection could not be '
            'established with the node_ip {}'.format(node_ip)
        )
    return False


def switchover(group, connection, logger):
    try:
        inner_logic.switchover(group, connection)
    except NoWriteNodeError:
        print_warning(
            'There isn\'t any node with the "read_write" mode. '
            'Check your configuration!'
        )
    except IsNotMasterMasterEnvironmentError:
        print_warning(
            'Switch not done! Slave is stopped or it`s not '
            'a master<->master replication.'
        )
        logger.warning(
            'Switch not done! Slave is stopped or it`s not '
            'a master<->master replication.'
        )
    except NodeWithDelayError:
        print_warning(
            'Switch not done! Node is delayed and cannot be set as read_write'
        )
        logger.error(
            'Switch not done! Node is delayed and cannot be set as read_write'
        )


def failover(group, connection, logger):
    try:
        inner_logic.failover(group, connection)
    except NoWriteNodeError:
        print_warning(
            'There isn\'t any node with the "read_write" mode. '
            'Check your configuration!'
        )
    except IsNotMasterMasterEnvironmentError:
        print_warning(
            'You have more than two nodes and we\'re not prepared to that.')
        logger.warning(
            'You have more than two nodes or it`s not a master<->master and '
            'we\'re not prepared to that'
        )
    except NodeIsDownError:
        print_error('ERROR -> The only candidate you have is unavailable!')
        logger.error('ERROR -> The only candidate you have is unavailable!')


def check_group_exist(name, connection, logger):
    try:
        inner_logic.get_group(name, connection)
        return True
    except GroupNotFoundError:
        print_warning(
            'There is no group_name identified by "{}"!'.format(name)
        )
        logger.error(
            'There is no group_name identified by "{}"'.format(name)
        )
        return False


def check_node_exist(group, node_ip, can_be_failed, connection, logger):
    try:
        node = inner_logic.get_node(group, node_ip, connection)
        if not can_be_failed and node.is_failed():
            raise NodeNotFoundError(node_ip, group)

        return True
    except NodeNotFoundError:
        print_warning(
            'The Ip: "{}" does not belongs to the group_name "{}" or '
            'it`s not enabled.'.format(node_ip, group)
        )
        logger.warning(
            'The Ip: "{}" does not belongs to the group_name "{}" or '
            'it`s not enabled.'.format(node_ip, group)
        )
        return False


def start(group_name, connection, logger):
    try:
        inner_logic.start(group_name, connection)
    except NoWriteNodeError:
        print_warning(
            'There isn\'t any node with the "read_write" mode. '
            'Check your configuration!'
        )
        logger.error(
            'FoxHa version cannot be initiated for '
            'group_name: "{}"'.format(group_name)
        )
    except ManyWriteNodesError:
        print_warning(
            'There is many nodes with the "read_write" mode. '
            'Check your configuration!'
        )
        logger.error(
            'FoxHa version cannot be initiated for '
            'group_name: "{}"'.format(group_name)
        )
    except NodeIsDownError:
        print_error('Connection could not established with write node')
        logger.error('Connection could not established with write node')
    else:
        logger.info('FoxHa initiated for group_name: {}'.format(group_name))


def config(group_name, connection, logger):
    try:
        group = inner_logic.get_group(group_name, connection)
    except GroupNotFoundError:
        print_warning(
            'There is no group_name identified by "{}"!'.format(group_name)
        )
        logger.error(
            'There is no group_name identified by "{}"'.format(group_name)
        )
    else:
        print \
            "GROUP_NAME: {}" \
            "\n\tDescription: {} " \
            "\n\tfqdn_vip: {} " \
            "\n\tmysql_adm_user: {}" \
            "\n\tmysql_repl_user: {}".format(
                group.name, group.description, group.vip_address,
                group.mysql_adm_user, group.mysql_repl_user
            )

        for node in group.nodes:
            print \
                "NODE: [{}]" \
                "\n\tip: {}" \
                "\n\tport: {}" \
                "\n\tmode: {}" \
                "\n\tstatus: {}".format(
                    node.name, node.ip, node.port,
                    node.fox_mode, node.fox_status
                )
