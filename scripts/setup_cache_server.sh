#!/bin/bash

export DEBIAN_FRONTEND=noninteractive

sudo apt-get -q -y update
sudo apt-get -q -y install build-essential

echo "INSTALLING PACKAGES"
sudo apt-get -q -y install memcached


#mysql_secure_installation

echo "ADJUSTING CONFIGURATION"
sudo sed -i 's/-l/# -l/' /etc/memcached.conf


echo "RESTARTING SERVICES"
sudo service memcached restart
