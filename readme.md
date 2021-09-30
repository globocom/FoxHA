# Introduction 
 
FoxHA was designed with the goal of replacing the Flipper as a more robust high availability 
solution, safer and inter­network. 
 
# Topology 
![image](https://user-images.githubusercontent.com/6109737/135170743-6e3e75da-c2fd-4990-b7c3-863b41f3063a.png)

 
# Requirements 
 FoxHA requires the following: 
● Red Hat Linux (or its derivatives), based on version 5 or above; 
● python >= 2.7.6 
● virtualenv >= 1.11.6 
 
## Python library requirements: 
● cffi==1.1.2 
● cryptography==0.8.1 
● enum34==1.0.4 
● MySQL­python==1.2.5 
● prettytable==0.7.2 
● pyasn1==0.1.8 
● pycparser==2.14 
● six==1.9.0 
 
Quick start 
 FoxHA is very simple. The best way to understand how it works is installing and using it. 
 
You can install it by: 
 
$ pip install foxha
log.txt 
 
After installing, for usage tips type: 
 
$ fox ­­help 
 
Understanding how it works 
 Foxha is an MySQL replication manager. This tool helps you to manage MySQL replication 
and watch the health of it. 
 
The main difference between FoxHA and the Flipper, is that for Flipper to work, requires the 
MySQL servers be part of the same network. 
 
The technology used for data replication is native to the DBMS itself, with its advantages and 
limitations. One characteristic of MySQL replication is the absence of conflict resolution, and 
this is the advantage of using the FoxHA as a replication manager. FoxHA manages on 
which node the application can write, and if necessary, allow the switching of the current 
write node in case of failure or maintenance, however avoiding data loss or application 
unavailability. 
 
Configuration 
 
VIP configuration and Health Check:  
 
● The health check will return 'WORKING’ only for the node that is read_write, and by 
definition, only one node has read_write enabled; 
● The connections are always directed only to one node, even if both hosts are with 
“WORKING" status (Health­check); 
● When the VIP is switched, connections to the last node are dropped 
(service­down­action reset); 
● The VIP is configured not to perform Failback; 
● Vip checking interval: 5 sec / Timeout for switching: 16 sec. 
 
Encryption file: 
 
Default path: ./config/.key 
 
The passwords saved at the database and specified at configuration file are encrypted using 
cryptography.fernet (symmetric encryption). So, for using foxha is necessary a encryption file 
containing the encryption key, by default at the path specified above. You can specify a 
different key file at command line using [­­keyfile] argument. 
 
Configurarion file: 
 
Default path: ./config/foxha_config.ini 
 
You can specify a different configuration file at command line using [­c/­­config] argument. 
 
Configuration file parameters: 
 
[repository]   
Host: ADDRESS_OF_MYSQL_REPOSITORY_DATABASE 
Port: MYSQL_PORT 
Database: REPOSITORY_DATABASE_NAME 
User: DBUSER 
Pass: ‘password’ 
 
Note: Password must be specified between single quotes. 
 
 
Logging: 
 
Default path: “./log/foxha_GROUP_NAME*.log” 
 
All commands/operations executed are logged, by default at the path specified above. You 
can specify a different log file name and path at command line using [­­logfile] argument. 
 
*GROUP_NAME= Group name specified at command line with option [­g/­­group]. 
 
Log rotation and retention: 
 
FoxHA has its own mechanism to manage log rotation and retention. It will keep up to 24 
hours (00:00:00 ­> 23:59:59) in the same log file, and one single file is created for each 
replication group managed. By default, 4 days will be kept in disc, plus the current log file. 
The default retention could be changed at command line using the [­­logretention] argument. 
 
FOXHA_HOME environment variable: 
 
FOXHA_HOME is an optional environment variable containing the base directory in which 
the foxha specific configuration file, key file and log file resides.  
 
If FOXHA_HOME is defined, the path for the configuration file, key file and log file will be as 
shown bellow: 
● Key file: $FOXHA_HOME/config/.key 
● Configuration file: $FOXHA_HOME/config/foxha_config.ini 
● Log file: $FOXHA_HOME/log/foxha_GROUP_NAME*.log 
 
*GROUP_NAME= Group name specified at command line with option [­g/—group]. 
 
Useful commands: 
 
List all replication groups registered: 
 
$ fox ­­list 
 
List all nodes at a specific group: 
 
$ fox ­­list ­g GROUP_NAME* 
 
Show the status of a specific group: 
 
$ fox ­­status ­g GROUP_NAME* 
 
Show the configuration of a specific group: 
 
$ fox ­­config ­g GROUP_NAME* 
 
Switch write and read node of a specific group: 
 
$ fox ­­switchover ­­group GROUP_NAME* 
 
or the short version 
 
$ fox ­­switch ­g GROUP_NAME* 
 
Set a specific node as the new read_write node of that group: 
 
$ fox ­g GROUP_NAME* ­n NODE_IP** ­­set read_write 
 
Specify a different path to the config file and to the log file: 
 
$ fox ­­status ­g GROUP_NAME* ­­configfile /tmp/foxha_config.ini ­­logfile /home/logfile.log 
 
*GROUP_NAME= Group name of a specific replication group. 
**NODE_IP= Node IP specified for a node in that group. 
