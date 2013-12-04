#!/bin/bash

export DEBIAN_FRONTEND=noninteractive

sudo apt-get -q -y update

echo "INSTALLING PACKAGES"
sudo apt-get -q -y install memcached
sudo apt-get -q -y install build-essential


#mysql_secure_installation

echo "ADJUSTING CONFIGURATION"
sudo sed -i 's/-l/# -l/' /etc/memcached.conf


echo "RESTARTING SERVICES"
sudo service memcached restart
