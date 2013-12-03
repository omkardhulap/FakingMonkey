#!/bin/bash

export DEBIAN_FRONTEND=noninteractive

sudo apt-get -q -y update

sudo debconf-set-selections <<< 'mysql-server-5.5 mysql-server/root_password password penguin'
sudo debconf-set-selections <<< 'mysql-server-5.5 mysql-server/root_password_again password penguin'

echo "INSTALLING PACKAGES"
sudo apt-get -q -y install mysql-server-5.5
sudo apt-get -q -y install memcached
sudo apt-get -q -y install build-essential


#mysql_secure_installation

echo "ADJUSTING CONFIGURATION"
sudo sed -i 's/-l/# -l/' /etc/memcached.conf
sudo sed -i 's/bind-address/# bind-address/' /etc/mysql/my.cnf
mysql -u root --password="penguin" -e 'GRANT ALL PRIVILEGES ON *.* TO root@"%" IDENTIFIED BY "penguin";'


echo "RESTARTING SERVICES"
sudo service memcached restart
