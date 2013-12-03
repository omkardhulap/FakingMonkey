import sys
import logging

import memcache
import MySQLdb as sql

import config


log = logging.getLogger('FakingMonkeyDAO')
log.setLevel('DEBUG')

class MemcachedDao:

    def __init__(self):
        log.info("Initializing kvstore connection")
        self.mc = memcache.Client(config.kv_store_addr)

        log.info("Initializing database connection")
        self.con = sql.connect(host=config.db_server_addr,
                               port=3306,
                               user='root',
                               passwd='penguin')

        cursor = self.con.cursor()

        query = ("CREATE DATABASE IF NOT EXISTS fakingmonkey;")
        cursor.execute(query)

        query = ("USE fakingmonkey;")
        cursor.execute(query)

        query = ("DROP TABLE IF EXISTS kvstore;")
        cursor.execute(query)

        query = ("CREATE TABLE kvstore(" \
                 "k VARCHAR({}) NOT NULL, " \
                 "v VARCHAR({}), " \
                 "PRIMARY KEY ( k ), " \
                 "UNIQUE ( k ));".format(config.key_size, config.value_size))
        cursor.execute(query)

        # prepopulate backend DB with keys


    def get(self, key):
        log.info("get key {}".format(key))
        value = self.mc.get(key)
        if not value:
            value = self._sql_get(key)
            self.mc.set(key, value)

        log.debug("returning value {}".format(value))
        return value


    def _sql_get(self, key):
        log.debug("sql get of key {}".format(key))
        cursor = self.con.cursor()
        query = "SELECT v FROM kvstore WHERE k=\"{}\";".format(key)
        cursor.execute(query)
        return cursor.fetchone()


    def set(self, key, value):
        log.info("set key {} as value {}".format(key, value))
        self._sql_set(key, value)
        self.mc.set(key, value)


    def _sql_set(self, key, value):
        log.debug("sql set k/v of {}/{}".format(key, value))
        cursor = self.con.cursor()
        query = ("INSERT INTO kvstore (k, v) "
                 "VALUES(\"{0}\",\"{1}\") "
                 "ON DUPLICATE KEY UPDATE v=\"{1}\";".format(key, value))
        cursor.execute(query)


    def __del__(self):
        try:
            self.con.close()
        except AttributeError:
            pass
