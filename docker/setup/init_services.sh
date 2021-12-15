#!/bin/bash

# Description: Entrypoint for FoxHA nodes containers

# USE the trap if you need to also do manual cleanup after the service is stopped,
#     or need to start multiple services in the one container
trap "echo TRAPed signal" HUP INT QUIT TERM

MYCNF='/etc/mysql/mysql.conf.d/foxha.cnf'
mysql_conn_string="mysql -uroot -ptest123 --silent --force -b"

# Define a random server_id for MySQL if not defined yet
grep -q -F "server_id" $MYCNF || echo "server_id = $RANDOM" >> $MYCNF

usermod -d /var/lib/mysql/ mysql



# Starting services
service ssh start
service monit start
service mysql start

# Execute script at /scripts directory with *.sh, *.sql and *.sql.gz extentions in alphabetical order
for f in /scripts/*; do
                        case "$f" in
                                *.sh)     echo "running $f"; . "$f" ;;
                                *.sql)    echo "running $f"; $mysql_conn_string < "$f"; echo ;;
                                *.sql.gz) echo "running $f"; gunzip -c "$f" | $mysql_conn_string; echo ;;
                                *)        echo "ignoring $f" ;;
                        esac
                        echo
                done

#echo "[hit enter key to exit] or run 'docker stop <container>'"
read

# stop service and clean up here
echo "stopping ssh"
service ssh stop
echo "stoping monit"
service monit stop
echo "stopping mysql"
service mysql stop

echo "exited $0"
