# -*- coding: utf-8 -*-

class Query:
    SHOW_SLAVE_STATUS = "SHOW SLAVE STATUS;"
    SHOW_GLOBAL_STATUS_SLAVE = "SHOW GLOBAL STATUS LIKE 'Slave_running';"
    SHOW_GLOBAL_STATUS_READ = "SHOW GLOBAL VARIABLES LIKE 'read_only';"
    SHOW_MASTER_STATUS = "SHOW MASTER STATUS;"
    SHOW_GLOBAL_SERVER_ID = "SHOW GLOBAL VARIABLES LIKE 'server_id';"
    SQL_MYSQL_VERSION = "SELECT SUBSTRING(@@version,1,3) as mysql_version;"
    SQL_REPO = "SELECT n.servername,n.node_ip,n.node_port,n.mode,g.mysql_adm_user,\
    g.mysql_adm_pass,g.mysql_repl_user,g.mysql_repl_pass FROM repl_nodes n \
    INNER JOIN repl_groups g ON g.group_name = n.group_name WHERE n.group_name='%s'\
    AND n.status='enabled' ORDER BY n.servername;"
    SQL_REPO_FULL = "SELECT n.servername,n.node_ip,n.node_port,n.mode,n.status,\
    g.mysql_adm_user,g.mysql_adm_pass,g.mysql_repl_user, g.mysql_repl_pass \
    FROM repl_nodes n INNER JOIN repl_groups g ON g.group_name = n.group_name \
    WHERE n.group_name='%s' AND n.status!='disabled' ORDER BY n.servername;"
    SQL_LIST = "SELECT g.group_name FROM repl_groups g ORDER BY g.group_name;"
    SQL_LIST_NODES = "SELECT n.group_name,n.servername,n.node_ip,n.status \
    FROM repl_nodes n WHERE n.group_name='%s' ORDER BY n.servername;"
    SQL_NODE_STATUS = "SELECT n.status, n.mode FROM repl_nodes n \
    WHERE n.group_name='%s' and n.node_ip='%s'"
    SQL_CONFIG_GROUP = "SELECT g.group_name, g.description, g.mysql_adm_user,\
    g.mysql_repl_user, g.vip_address FROM repl_groups g where g.group_name = '%s';"
    SQL_CONFIG_NODES = "SELECT g.group_name,n.servername,n.node_ip,n.node_port,n.mode,n.status \
    FROM repl_nodes n INNER JOIN repl_groups g ON g.group_name = n.group_name \
    where n.group_name = '%s' ORDER BY n.servername;"

    SQL_GROUP_EXIST = \
        'SELECT g.group_name FROM repl_nodes n INNER JOIN repl_groups g ' \
        'ON g.group_name = n.group_name WHERE n.group_name = "%s" limit 1;'

    SQL_GROUP_ADDED = "SELECT g.group_name FROM repl_groups g " \
                      "WHERE g.group_name = '%s' limit 1;"

    SQL_NODE_EXIST = "SELECT node_ip FROM repl_nodes where group_name = '%s' AND node_ip = '%s';"
    SQL_NODE_EXIST_WITHOUT_FAILED = "SELECT node_ip FROM repl_nodes where status = 'enabled'\
    AND group_name = '%s' AND node_ip = '%s';"
    SQL_NODES_WITHOUT_WRITEONE = "SELECT n.group_name,n.servername,n.node_ip,n.node_port,\
    n.status,n.mode,g.mysql_adm_user,g.mysql_adm_pass,g.mysql_repl_user, g.mysql_repl_pass \
    FROM repl_nodes n INNER JOIN repl_groups g ON g.group_name = n.group_name \
    WHERE n.status='enabled' and n.group_name='%s' and n.node_ip != '%s' ORDER BY n.servername;"
    SET_MODE = "SET GLOBAL read_only=%s;"
    UPDATE_STATE = "UPDATE repl_nodes n SET n.status='%s' WHERE n.node_ip='%s' and n.group_name='%s';"
    UPDATE_MODE = "UPDATE repl_nodes n SET n.mode='%s' WHERE n.node_ip='%s' and n.group_name='%s';"
    SQL_CHECK_WRITE = "SELECT n.servername,n.node_ip,n.node_port,n.mode,g.mysql_adm_user,\
    g.mysql_adm_pass,g.mysql_repl_user, g.mysql_repl_pass FROM repl_nodes n \
    INNER JOIN repl_groups g ON g.group_name = n.group_name \
    WHERE n.group_name='%s'AND n.status='enabled' AND n.mode='read_write';"
    SQL_GET_CREDENTIAL = "SELECT n.servername,n.node_ip,n.node_port,n.mode,g.mysql_adm_user,\
    g.mysql_adm_pass,g.mysql_repl_user,g.mysql_repl_pass FROM repl_nodes n \
    INNER JOIN repl_groups g ON g.group_name = n.group_name \
    where n.group_name='%s' AND n.node_ip='%s';"
    SQL_STATUS_HEARTBEAT="SELECT DATE_FORMAT(t.ts, '%Y-%m-%d %H:%i:%S') as last_update FROM heartbeat.heartbeat t;"
    SQL_NODE_DETAILS="SELECT n.servername, n.node_port, g.mysql_adm_user, g.mysql_adm_pass \
    FROM repl_nodes n INNER JOIN repl_groups g \
    ON n.group_name = g.group_name where n.group_name = '%s' and n.node_ip = '%s'"

    SQL_INSERT_GROUP = \
        'INSERT INTO repl_groups (group_name, description, vip_address, ' \
        'mysql_adm_user, mysql_adm_pass, mysql_repl_user, mysql_repl_pass) ' \
        'VALUES ("{}", "{}", "{}", "{}", "{}", "{}", "{}");'

    SQL_DELETE_GROUP = 'DELETE FROM repl_groups WHERE group_name = "{}"'

    SQL_INSERT_NODE = \
        'INSERT INTO repl_nodes (group_name, servername, node_ip, ' \
        'node_port, mode, status, timestamp) ' \
        'VALUES ("{}", "{}", "{}", "{}", "{}", "{}", now());'

    SQL_DELETE_NODE = \
        'DELETE FROM repl_nodes ' \
        'WHERE group_name = "{}" AND node_ip = "{}" '

    SQL_STOP_SLAVE = "STOP SLAVE"

    SQL_START_SLAVE = "START SLAVE"
