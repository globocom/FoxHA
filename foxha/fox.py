# -*- coding: utf-8 -*-

from os import sys
from os import getenv
import argparse
from foxha import __version__
from .print_format import print_warning
from .query import Query
from .utils import Utils
import formatter
import connection

# Initializing global constants
CIPHER_SUITE = None
LOGGER = None
CONNECTION = None


def check_node_exist(group_name, nodeip, plus_failed=False):
    return formatter.check_node_exist(
        group_name, nodeip, plus_failed, CONNECTION, LOGGER
    )


def set_read_only(group_name, nodeip):
    return formatter.set_read_only(group_name, nodeip, CONNECTION, LOGGER)


def set_read_write(group_name, nodeip):
    return formatter.set_read_write(group_name, nodeip, CONNECTION, LOGGER)


def switchover(group_name):
    formatter.switchover(group_name, CONNECTION, LOGGER)


def failover(group_name):
    formatter.failover(group_name, CONNECTION, LOGGER)


def set_status(group_name, nodeip, status):
    node_write = formatter.check_write(group_name, CONNECTION, LOGGER)
    if status == 'enabled':
        CONNECTION.query(Query.UPDATE_STATE % (status, nodeip, group_name))
        LOGGER.info(
            "Node: \"%s\" enabled at group_name: \"%s\"." %
            (nodeip, group_name))
    if node_write:
        if status == 'disabled':
            if node_write.ip == nodeip:
                print_warning(("The \"{}\" is the current read_write "\
                "node at group_name \"{}\" and cannot be disabled.").format(nodeip,\
                group_name))
                LOGGER.warning(
                    "The \"%s\" is the current read_write node at group_name \
                    \"%s\" and cannot be disabled." %
                    (nodeip, group_name))
            else:
                CONNECTION.query(Query.UPDATE_STATE % (status, nodeip, group_name))
                LOGGER.info(
                    "Node: \"%s\" disabled at group_name: \"%s\"." %
                    (nodeip, group_name))
        if status == 'failed':
            if node_write.ip == nodeip:
                failover(group_name)
            else:
                CONNECTION.query(Query.UPDATE_STATE % (status, nodeip, group_name))
    else:
        CONNECTION.query(Query.UPDATE_STATE % (status, nodeip, group_name))


def set(set, group_name, nodeip):
    if set == 'read_only':
        set_read_only(group_name, nodeip)
    elif set == 'read_write':
        set_read_write(group_name, nodeip)
    elif set == 'disabled' or set == 'failed' or set == 'enabled':
        set_status(group_name, nodeip, set)


def fox_arg_parse():
    parser = argparse.ArgumentParser(
        add_help=True,
        description="Description: MySQL FoxHA Administration")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '--version',
        action='version',
        version='%(prog)s ' +
        __version__)
    group.add_argument(
        "--status",
        help="show the status of a group_name",
        action="store_true")
    group.add_argument(
        "-l",
        "--list",
        help="lists the available group_names and nodes if [-g/--group] is specified",
        action="store_true")
    group.add_argument(
        "-c",
        "--config",
        help="show the config of a group_name",
        action="store_true")
    group.add_argument(
        "--start",
        help="check who is the read_write node and enable it at that node",
        action="store_true")
    group.add_argument(
        "--switchover",
        help="switchover to a new master",
        action="store_true")
    group.add_argument(
        "--failover",
        help="failover to a new master",
        action="store_true")
    group.add_argument(
        "--set",
        choices=[
            "read_write",
            "read_only",
            "failed",
            "disabled",
            "enabled"],
        action="store")
    parser.add_argument(
        "-g",
        "--group",
        metavar='GROUP_NAME',
        help="use to specify a group_name",
        action="store")
    parser.add_argument(
        "-n",
        "--nodeip",
        help="use to specify a node ip",
        action="store")
    parser.add_argument(
        "--keyfile",
        help="different path to key file - Default: ./config/.key",
        action="store")
    parser.add_argument(
        "--configfile",
        help="different path to config file - Default: ./config/foxha_config.ini",
        action="store")
    parser.add_argument(
        "--logfile",
        help="different path to log file - Default: ./log/foxha_[group_name].log",
        action="store")
    parser.add_argument(
        "--logretention",
        type=int,
        help="log file retention in days - Default: 4 days plus current",
        action="store")
    return parser


def main(values=None):
    args = fox_arg_parse().parse_args(values)
    argument_vars = vars(args)

    # Parsing Env. Variable FOXHA_HOME
    foxha_home = getenv('FOXHA_HOME')

    # Key file argument
    global CIPHER_SUITE
    if args.keyfile:
        CIPHER_SUITE = Utils.parse_key_file(args.keyfile)
    elif foxha_home:
        keyfile = foxha_home + '/config/.key'
        CIPHER_SUITE = Utils.parse_key_file(keyfile)
    else:
        CIPHER_SUITE = Utils.parse_key_file()

    # Config file argument
    config_file = './config/foxha_config.ini'
    if args.configfile:
        config_file = args.configfile
    elif foxha_home:
        config_file = foxha_home + '/config/foxha_config.ini'

    global CONNECTION
    CONNECTION = connection.from_config_file(CIPHER_SUITE, config_file)

    # Defining logfile name
    global LOGGER
    if args.group:
        logname = './log/foxha_' + args.group.lower() + '.log'
        if foxha_home:
            logname = foxha_home + '/log/foxha_' + \
                args.group.lower() + '.log'
    else:
        logname = '/tmp/foxha.log'

    if args.logfile and args.logretention:
        LOGGER = Utils.logfile(args.logfile, args.logretention)
    if args.logfile or args.logretention:
        if args.logfile:
            LOGGER = Utils.logfile(args.logfile)
        if args.logretention:
            LOGGER = Utils.logfile(logname, args.logretention)
    else:
        LOGGER = Utils.logfile(logname)

    if args.nodeip and args.set is None:
        print_warning("[-n/--node] specified out of context.")
        exit(1)

    if args.list:
        if args.group:
            formatter.list_nodes(args.group.lower(), CONNECTION)
        else:
            formatter.list_group(CONNECTION)

    if args.group:
        if argument_vars.values().count(True) == 0 and args.set is None:
            print_warning("You could not specify [-g/--group] alone")
            exit(1)
        else:
            arg_group_name = args.group.lower()
            if formatter.check_group_exist(arg_group_name, CONNECTION, LOGGER):
                pass
    else:
        print_warning("Group_name not specified. Use [-g/--group] to "\
        "specify the group_name")
        exit(2)

    if args.set:
        if args.nodeip:
            if args.set in ('disabled', 'enabled', 'failed', 'read_only'):
                if check_node_exist(arg_group_name, args.nodeip, plus_failed=True):
                    set(args.set, arg_group_name, args.nodeip)
            else:  # args.set in ('read_write')
                if check_node_exist(arg_group_name, args.nodeip, plus_failed=False):
                    set(args.set, arg_group_name, args.nodeip)
        else:
            print_warning("You must specify a [-n/--node] to the [--set] command.")
            exit(1)

    if args.status:
        formatter.status_nodes(arg_group_name, LOGGER, CONNECTION)

    if args.switchover:
        switchover(arg_group_name)

    if args.failover:
        failover(arg_group_name)

    if args.start:
        formatter.start(arg_group_name, CONNECTION, LOGGER)

    if args.config:
        formatter.config(arg_group_name, CONNECTION, LOGGER)


if __name__ == '__main__':
    main()
