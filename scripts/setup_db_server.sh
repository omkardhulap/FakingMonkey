#!/bin/bash

export DEBIAN_FRONTEND=noninteractive

sudo apt-get -q -y update

sudo debconf-set-selections <<< 'mysql-server-5.5 mysql-server/root_password password B8B274C6AF8165B631B4B517BD0ED2694909F464'
sudo debconf-set-selections <<< 'mysql-server-5.5 mysql-server/root_password_again password B8B274C6AF8165B631B4B517BD0ED2694909F464'

echo "INSTALLING DB PACKAGES"
sudo apt-get -q -y install mysql-server-5.5
sudo apt-get -q -y install build-essential


#mysql_secure_installation

echo "ADJUSTING DB CONFIGURATION"
sudo sed -i 's/bind-address/# bind-address/' /etc/mysql/my.cnf
mysql -u root --password="B8B274C6AF8165B631B4B517BD0ED2694909F464" -e 'GRANT ALL PRIVILEGES ON *.* TO root@"%" IDENTIFIED BY "penguin";'

mysql -u root --password="B8B274C6AF8165B631B4B517BD0ED2694909F464" -e 'CREATE USER newrelic@54.212.250.133 IDENTIFIED BY PASSWORD "penguin";'
mysql -u root --password="B8B274C6AF8165B631B4B517BD0ED2694909F464" -e 'GRANT PROCESS,REPLICATION CLIENT ON *.* TO newrelic@54.212.250.133;'

