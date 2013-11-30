import sys
import logging

import memcache
import MySQLdb as sql

import config


class MemcachedDao:

    log = logging.getLogger('FakingMonkey')
    log.setLevel('DEBUG')

    def __init__(self):
        self.mc = memcache.Client(config.kv_store_addr_list)
        self.con = sql.connect(config.db_addr, 'root', 'penguin', 'fakingmonkey')

        cursor = self.con.cursor()
        query = ("DROP TABLE 'kvstore';")
        cursor.execute(query)

        query = ("CREATE TABLE 'kvstore' "
                 "('key' CHAR({}), 'value' CHAR({}), "
                 "PRIMARY KEY ('key'), "
                 "UNIQUE ('key'));".format(config.key_size, config.value_size))
        cursor.execute(query)

        # prepopulate backend DB with keys


    def get(self, key):
        value = self.mc.get(key)
        if not value:
            value = self._sql_get(key)
            self.mc.set(key, value)
            return value

    def _sql_get(self, key):
        log.debug("sql get of key {}".format(key))
        cursor = self.con.cursor()
        query = "SELECT 'value' FROM 'kvstore' WHERE 'key'='{}';".format(key)
        cursor.execute(query)
        return cursor.fetchone()

    def set(self, key, value):
        self._sql_set(key, value)
        self.mc.set(key, value)

    def _sql_set(self, key, value):
        log.debug("sql set k/v of {}/{}".format(key, value))
        cursor = self.con.cursor()
        query = ("INSERT INTO 'kvstore' ('key', 'value') "
                 "VALUES('{1}','{2}') "
                 "ON DUPLICATE KEY UPDATE 'value'='{2}';".format(key, value)
        cursor.execute(query)

    def __del__(self):
        self.con.close()
