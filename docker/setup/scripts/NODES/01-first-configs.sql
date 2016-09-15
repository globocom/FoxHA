-- Create users
CREATE USER IF NOT EXISTS 'heartbeat'@'%' IDENTIFIED BY "heartbeat";
-- GRANT REPLICATION CLIENT ON *.* TO 'heartbeat'@'%';
GRANT ALL PRIVILEGES ON `heartbeat`.* TO 'heartbeat'@'%';
CREATE USER IF NOT EXISTS 'u_repl'@'%' IDENTIFIED BY "u_repl";
GRANT REPLICATION SLAVE, REPLICATION CLIENT ON *.* TO 'u_repl'@'%';

GRANT ALL PRIVILEGES ON *.* TO 'foxha'@'%' IDENTIFIED BY "foxha" WITH GRANT OPTION;

-- Fixing permissions for root
USE mysql; UPDATE user SET host="%" WHERE user="root" AND host="localhost"; 
DELETE FROM user WHERE host != "%" AND user="root"; FLUSH PRIVILEGES;

-- Create heartbeat table
CREATE SCHEMA IF NOT EXISTS heartbeat DEFAULT CHARACTER SET utf8;

DROP TABLE IF EXISTS heartbeat.heartbeat;

CREATE TABLE IF NOT EXISTS heartbeat.heartbeat (id int NOT NULL PRIMARY KEY, ts datetime NOT NULL);

USE heartbeat; INSERT INTO heartbeat (ts, id) VALUES (NOW(),1);
