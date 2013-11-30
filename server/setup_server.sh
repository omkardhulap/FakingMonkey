#!/bin/bash
sudo apt-get update
sudo apt-get install mysql-server
sudo apt-get install memcached
sudo apt-get install build-essential
sudo pecl install memcache


#mysql_secure_installation

sudo service memcached restart



mysql -u root -p -e "use test;

grant all on test.* to test@localhost identified by 'testing123';

create table example (id int, name varchar(30));

insert into example values (1, \"new_data\");

exit;"




sudo mv memcache.php memstats.php /var/www/
