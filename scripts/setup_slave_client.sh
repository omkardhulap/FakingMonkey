#!/bin/bash
sudo apt-get -q update
sudo apt-get -y -q install locustio
sudo apt-get -y -q install python-mysqldb
sudo pip install memcached

# Install FakingMonkey
echo "Installing FakingMonkey"
rm -r FakingMonkey-deploy
sudo apt-get -y -q install unzip
wget https://github.com/djmailhot/FakingMonkey/archive/deploy.zip
unzip deploy.zip

echo "Starting up FakingMonkey"
./FakingMonkey-deploy/FakingMonkey
