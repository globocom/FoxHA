#!/bin/bash

#"::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::"
#"| Script for initialization of FoxHA test environment
#"| Created by: Rafael Dantas"
#"| Email: rafael.dantas@corp.globo.com
#"::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::"


########################################
# Parameters received by script 
########################################
#$1 - start/stop

ACTION=$(echo $1 | tr "A-Z" "a-z")

#Help
if [ -z $ACTION ]; then
	echo "The script should be execute as below:\n"
	echo "Sintax: $0 [start|stop]\n"
	exit 1
fi

docker_start()
{
   cd docker/ && docker-compose up --build -d
   cd ..
}

docker_stop()
{
   cd docker/ && docker-compose stop
   cd ..
}

config_mysql_repl()
{

NODE_NAME=$1
NODE_PORT=$2
REPL_NODE_MASTER=$3
CONNECT_TIMEOUT=30
MYSQL_USER="root"
MYSQL_PASS="test123"

IP_NODE_MASTER=$(echo $(docker inspect $REPL_NODE_MASTER | grep -e \"IPAddress | sed 's/^ *//' | uniq | tr -d ","\"" " | cut -d":" -f2))

echo "Configuring replication master at container: $NODE_NAME"

#Checking if mysql db1 is already up
CONNECT_SUCCESS=1
COUNT=0
while [ $CONNECT_SUCCESS -ne 0 ]
do
	let "COUNT++"
	if [ $CONNECT_TIMEOUT -lt $COUNT ]; then
        echo "ERROR: Connection timeout to mysql => $NODE_NAME:$NODE_PORT"
        exit 1
    fi
	echo "Trying to connect to mysql: $NODE_NAME... $COUNT"
	mysql -h $NODE_NAME -P $NODE_PORT -u $MYSQL_USER -p$MYSQL_PASS -e 'exit' 2> /dev/null
	CONNECT_SUCCESS=$?
	sleep 1
done

#Checking if replication is already configured
REPL_CONFIG=$(mysql -h $NODE_NAME -P $NODE_PORT -u $MYSQL_USER -p$MYSQL_PASS -e 'show slave status;')

if [ -z "${REPL_CONFIG}" ]; then
mysql -h $NODE_NAME -P $NODE_PORT -u root -p$MYSQL_PASS << EOF
CHANGE MASTER TO MASTER_HOST="$IP_NODE_MASTER", MASTER_USER='u_repl', MASTER_PASSWORD='u_repl', MASTER_AUTO_POSITION=1;
START SLAVE;
EOF
fi

if [ $NODE_NAME == 'db1' ]; then
	mysql -h $NODE_NAME -P $NODE_PORT -u $MYSQL_USER -p$MYSQL_PASS -e 'SET GLOBAL read_only=OFF;'
fi

}

#######################################
##               MAIN                ##
#######################################

if [ $ACTION == "start" ]; then
    docker_start
    config_mysql_repl db1 3308 db2
    config_mysql_repl db2 3310 db1
else
    docker_stop
fi

###########################################################
#END
###########################################################