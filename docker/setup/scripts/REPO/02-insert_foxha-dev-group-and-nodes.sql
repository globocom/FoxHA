/*
*/
INSERT INTO `repl_groups` (`group_name`,`description`,`vip_address`,`mysql_adm_user`,`mysql_adm_pass`,`mysql_repl_user`,`mysql_repl_pass`) VALUES ('foxha-dev','foxha-dev.mysql.example.com','10.x.x.x','foxha','gAAAAABX2a-t_a-L6IRtW4nqLvHUhH8t9ZlyFTRg9EjUjdslpzn1hg7U9KdUW5JL18xsKA8xcwF1V0o24UjTgbrdV0c5TPMcZw==','u_repl','gAAAAABX2a-8rIXdQ4_RmI15GEVhLKD132ewNFp_KUztmnHPTA6N85Aqx-cuRzGz_-3GoGHZS7onfhpSF86R-k8tKC2agaXSzA==');

INSERT INTO `repl_nodes` (`group_name`,`servername`,`node_ip`,`node_port`,`mode`,`status`,`timestamp`) VALUES ('foxha-dev','db1.local','db1',3308,'read_write','enabled','2016-08-29 17:04:13');
INSERT INTO `repl_nodes` (`group_name`,`servername`,`node_ip`,`node_port`,`mode`,`status`,`timestamp`) VALUES ('foxha-dev','db2.local','db2',3310,'read_only','enabled','2016-08-29 17:04:14');
