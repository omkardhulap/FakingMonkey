#!/bin/bash

sudo su

# Install FakingMonkey
echo "INSTALLING FAKINGMONKEY"
rm -r FakingMonkey-deploy
apt-get -y -q install unzip
wget https://github.com/djmailhot/FakingMonkey/archive/deploy.zip
unzip deploy.zip

# Install new relic
echo "INSTALLING NEWRELIC"
echo "deb http://apt.newrelic.com/debian/ newrelic non-free" >> /etc/apt/sources.list
wget -O- https://download.newrelic.com/548C16BF.gpg | apt-key add -
apt-get -q update
apt-get -q -y install newrelic-sysmond
nrsysmond-config --set license_key=846a0af02ab8542c0b6f81256bd7cc127f4b8546

# Initialize this node as a newrelic server
apt-get -q -y install python-pip
pip install newrelic
newrelic-admin generate-config 846a0af02ab8542c0b6f81256bd7cc127f4b8546 newrelic.ini


# Installing mysql monitoring
echo "INSTALLING mysql monitoring"
apt-get install -q -y openjdk-7-jre-headless
wget -O newrelic_mysql.tar.gz https://rpm.newrelic.com/plugins/52/f6f6508827727a34e847c5694a5ab89b
tar -xvf newrelic_mysql.tar.gz

# Config newrelic mysql monitoring
cd newrelic_mysql_plugin-1.1.0
cd config
echo "licenseKey=846a0af02ab8542c0b6f81256bd7cc127f4b8546" > newrelic.properties
cp template_mysql.instance.json mysql.instance.json
sed -i 's/Localhost/db_server/' mysql.instance.json
sed -i 's/localhost/54.203.245.132/' mysql.instance.json
sed -i 's/USER_NAME_HERE/newrelic/' mysql.instance.json
sed -i 's/USER_PASSWD_HERE/penguin/' mysql.instance.json
cp example_logging.properties logging.properties
cd ..
java -jar newrelic_mysql_plugin-1.1.0.jar &
cd ..


# Setup the FakingMonkey deployment to use newrelic
echo "STARTING UP FAKINGMONKEY"
NEW_RELIC_CONFIG_FILE=newrelic.ini
export NEW_RELIC_CONFIG_FILE
newrelic-admin run-program source ~/FakingMonkey-deploy/FakingMonkey

/etc/init.d/newrelic-sysmond start

