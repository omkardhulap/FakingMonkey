#!/bin/bash
sudo apt-get -q update
sudo apt-get -q -y install build-essential
sudo apt-get -q -y install python-pip

echo "INSTALLING LIBRARIES"
sudo apt-get -y -q install python-dev
sudo apt-get -y -q install libevent-dev
sudo pip freeze locustio /tmp/reqs.txt
sudo pip install -r /tmp/reqs.txt
sudo pip install locustio
sudo apt-get -y -q install python-mysqldb
sudo pip install python-memcached

# Install FakingMonkey
echo "INSTALLING FAKINGMONKEY"
sudo rm -r FakingMonkey-deploy
sudo apt-get -y -q install unzip
sudo rm deploy.zip
wget https://github.com/djmailhot/FakingMonkey/archive/deploy.zip
unzip deploy.zip

echo "Starting up FakingMonkey"
(cd FakingMonkey-deploy && ./FakingMonkey)
