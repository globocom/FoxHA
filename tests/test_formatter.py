from foxha import fox
from foxha import formatter
from foxha import inner_logic
from foxha.query import Query
import test_utils


def build_message(group, node):
    return 'The Ip: "{}" does not belongs to the group_name "{}" or ' \
           'it`s not enabled.'.format(node, group)


def setup_module(module):
    test_utils.connect_database()


def teardown_module(module):
    test_utils.reset_database()


def setup_function(module):
    test_utils.reset_database()


def test_check_group_exist(environment, default_connection, default_logger):
    assert formatter.check_group_exist(
        environment.group, default_connection, default_logger
    )


def test_check_group_not_exist(
        environment, capsys, default_connection, default_logger
):
    assert not formatter.check_group_exist(
        'Strange_Group_Env', default_connection, default_logger
    )
    message = 'There is no group_name identified by "Strange_Group_Env"!'

    out, err = capsys.readouterr()
    assert message in out


def test_check_node_exist(environment):
    assert fox.check_node_exist(
        environment.group, environment.replication, False
    )


def test_check_failed_node_exist(environment, capsys):
    test_utils.failed_node(environment.replication, capsys)
    assert fox.check_node_exist(
        environment.group, environment.replication, True
    )


def test_check_failed_node_not_exist(environment, capsys):
    test_utils.failed_node(environment.replication, capsys)
    assert not fox.check_node_exist(
        environment.group, environment.replication, False
    )
    out, err = capsys.readouterr()
    assert build_message(environment.group, environment.replication) in out


def test_check_node_not_exist_without_failed(environment, capsys):
    assert not fox.check_node_exist(
        'Strange_Group_Env', '987.654.321.666', False
    )
    out, err = capsys.readouterr()
    assert build_message('Strange_Group_Env', '987.654.321.666') in out


def test_check_node_not_exist_with_failed(environment, capsys):
    assert not fox.check_node_exist(
        'Strange_Group_Env', '987.654.321.666', True
    )

    out, err = capsys.readouterr()
    assert build_message('Strange_Group_Env', '987.654.321.666') in out


def test_check_node_not_exist_wrong_group_without_failed(environment, capsys):
    assert not fox.check_node_exist(
        'Strange_Group_Env', environment.replication, False
    )
    out, err = capsys.readouterr()
    assert build_message('Strange_Group_Env', environment.replication) in out


def test_check_node_not_exist_wrong_group_with_failed(environment, capsys):
    assert not fox.check_node_exist(
        'Strange_Group_Env', environment.replication, True
    )

    out, err = capsys.readouterr()
    assert build_message('Strange_Group_Env', environment.replication) in out


def test_check_node_not_exist_wrong_ip_without_failed(environment, capsys):
    assert not fox.check_node_exist(
        environment.group, '123.123.123.123', False
    )
    out, err = capsys.readouterr()
    assert build_message(environment.group, '123.123.123.123') in out


def test_check_node_not_exist_wrong_ip_with_failed(environment, capsys):
    assert not fox.check_node_exist(
        environment.group, '123.123.123.123', True
    )

    out, err = capsys.readouterr()
    assert build_message(environment.group, '123.123.123.123') in out


def test_can_start_group(environment, default_connection, default_logger):
    node_write = formatter.check_write(
        environment.group, default_connection, default_logger
    )
    node_write.node_connection.query(Query.SET_MODE % 'ON')
    assert node_write.mode != node_write.fox_mode

    formatter.start(environment.group, default_connection, default_logger)
    assert node_write.mode == node_write.fox_mode


def test_cannot_start_group_without_write(
        environment, capsys, default_connection, default_logger
):
    node_write = formatter.check_write(
        environment.group, default_connection, default_logger
    )
    node_write.fox_connection.query(
        Query.UPDATE_MODE % ('read_only', node_write.ip, node_write.group)
    )
    assert node_write.mode != node_write.fox_mode

    formatter.start(environment.group, default_connection, default_logger)
    out, err = capsys.readouterr()
    assert \
        'There isn\'t any node with the "read_write" mode. ' \
        'Check your configuration!' in out


def test_cannot_start_group_with_many_write(
        environment, capsys, default_connection, default_logger
):
    node_repl = inner_logic.get_node(
        environment.group, environment.replication, default_connection
    )
    node_repl.fox_connection.query(
        Query.UPDATE_MODE % ('read_write', node_repl.ip, node_repl.group)
    )
    assert node_repl.mode != node_repl.fox_mode

    formatter.start(environment.group, default_connection, default_logger)
    out, err = capsys.readouterr()
    assert 'There is many nodes with the "read_write" mode. ' \
           'Check your configuration!' in out

    node_repl.fox_connection.query(
        Query.UPDATE_MODE % ('read_only', node_repl.ip, node_repl.group)
    )
    assert node_repl.mode == node_repl.fox_mode


def test_cannot_start_with_master_node_down(
        environment, capsys, default_connection, default_logger
):
    node_write = formatter.check_write(
        environment.group, default_connection, default_logger
    )
    assert node_write.is_mysql_status_up()

    test_utils.deactivate_node(environment.master_node)
    assert node_write.is_mysql_status_down()

    formatter.start(environment.group, default_connection, default_logger)
    out, err = capsys.readouterr()
    assert 'Connection could not established with write node' in out

    test_utils.activate_node(environment.master_node)


def test_can_print_config(
        environment, capsys, default_connection, default_logger
):
    formatter.config(environment.group, default_connection, default_logger)
    out, err = capsys.readouterr()

    assert "GROUP_NAME: {}".format(environment.group) in out
    assert "Description: {}".format(environment.description) in out
    assert "fqdn_vip: {}".format(environment.vip_address) in out
    assert "mysql_adm_user: {}".format(environment.mysql_adm_user) in out
    assert "mysql_repl_user: {}".format(environment.mysql_repl_user) in out
    assert out.count('NODE: [') == len(environment.nodes)


def test_cannot_print_config_to_external_node(
        environment, capsys, default_connection, default_logger
):
    formatter.config('Strange_Group_Env', default_connection, default_logger)
    out, err = capsys.readouterr()

    message = 'There is no group_name identified by "Strange_Group_Env"!'
    assert message in out
