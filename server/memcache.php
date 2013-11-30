<?php
/*
$MEMCACHE_SERVERS = array(
    "10.1.1.1", //web1
    "10.1.1.2", //web2
    "10.1.1.3", //web3 
); 
$memcache = new Memcache();
foreach($MEMCACHE_SERVERS as $server){
    $memcache->addServer ( $server ); 
}
*/


$memcache = new Memcache();
$memcache->pconnect('localhost', 11211);

mysql_connect("localhost", "test", "testing123") or die(mysql_error());
mysql_select_db("test") or die(mysql_error());

$query = "select id from example where name = 'new_data'";
$querykey = "KEY" . md5($query);

$result = $memcache->get($querykey);

if (!$result) {
       $result = mysql_fetch_array(mysql_query("select id from example where name = 'new_data'")) or die('mysql error');
       $memcache->set($querykey, $result, 0, 600);
print "got result from mysql\n";
return 0;
}

print "got result from memcached\n";
return 0;

?>
