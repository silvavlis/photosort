# -*- mode: python; coding: utf-8 -*-
from __future__ import print_function


__author__ = "Miguel Angel Ajo Pelayo"
__email__ = "miguelangel@ajo.es"
__copyright__ = "Copyright (C) 2013 Miguel Angel Ajo Pelayo"
__license__ = "GPLv3"

import sqlite3
import logging
import os.path

class PhotoDB:
    def __init__(self, config):
        self._db_file = config.db_file()
        if not os.path.isfile(self._db_file):
            self.initialize()
        self._dbconn = sqlite3.connect(self._db_file)
        self._curs = self._dbconn.cursor()
        self._output_dir = config.output_dir()
        self._file_mode = config.output_chmod()

    def __del__(self):
        self._dbconn.commit()
        self._curs.close()
        self._dbconn.close()

    def initialize(self):
        logging.debug("initializing DB %s" %
                      (self._db_file))
        tables = [
            "CREATE TABLE hash (value TEXT PRIMARY KEY ASC);",
            "CREATE TABLE file_type (type TEXT PRIMARY KEY ASC);",
            "CREATE TABLE directory (name TEXT PRIMARY KEY ASC);",
            '''CREATE TABLE file (name TEXT PRIMARY KEY ASC, hash_id INTEGER, 
                    dir_id INTEGER, type_id INTEGER, 
                    FOREIGN KEY(hash_id) REFERENCES hash(rowid), 
                    FOREIGN KEY(dir_id) REFERENCES directory(rowid), 
                    FOREIGN KEY(type_id) REFERENCES file_type(rowid));'''
        ]
        views = [
            '''CREATE VIEW file_props AS SELECT file.name, directory.name, 
                    file_type.type, hash.value FROM file 
                    INNER JOIN directory ON file.dir_id = directory.rowid 
                    INNER JOIN hash ON file.hash_id = hash.rowid 
                    INNER JOIN file_type ON file.type_id = file_type.rowid;'''
        ]

        dbconn = sqlite3.connect(self._db_file)
        curs = dbconn.cursor()
        for table_spec in tables:
            curs.execute(table_spec)
        for view_spec in views:
            curs.execute(view_spec)
        dbconn.commit()
        curs.close()
        dbconn.close()

    def _get_id_or_insert(self, table, column, value):
        insert_stmt = "INSERT INTO {table}({column}) VALUES (:value);".\
                format(table=table, column=column)
        select_stmt = "SELECT rowid FROM {table} WHERE {column}=:value;".\
                format(table=table, column=column) 
        try:
            self._curs.execute(insert_stmt, {"value": value})
            return self._curs.lastrowid
        except sqlite3.IntegrityError as e:
            if str(e).startswith("column ") and str(e).endswith(" is not unique"):
                self._curs.execute(select_stmt, {"value": value})
                return self._curs.fetchone()[0]

    def add_to_db(self, file_dir, file_name, media_file):
        logging.debug("adding %s/%s" %
                      (file_dir, file_name))

        try:
            hash = media_file.hash()
        except IOError as e:
            logging.error("IOError %s trying to hash %s" %
                          (e,media_file.get_path()))
            return False
        hash_id = self._get_id_or_insert("hash", "value", hash)

        file_type = media_file.type()
        type_id = self._get_id_or_insert("file_type", "type", file_type)

        # remove output dir path + '/'
        file_dir = file_dir[len(self._output_dir) + 1:]
        dir_id = self._get_id_or_insert("directory", "name", file_dir)

        self._curs.execute("INSERT INTO file(name, hash_id, type_id, dir_id) " +
                "VALUES (:filename, :hash_id, :type_id, :dir_id);", \
                {"filename": file_name, "hash_id": hash_id, \
                "type_id": type_id, "dir_id": dir_id})
        file_id = self._curs.lastrowid

        self._dbconn.commit()

        logging.info("indexed %s/%s %s %s" % (file_dir,
                                              file_name,
                                              file_type,
                                              hash))
        return True

    def is_duplicate(self, media_file):
        """
        checks if the given file has been already sorted
        returns True if so, False if not
        """
        hash = media_file.hash()

        self._curs.execute("SELECT * FROM hash WHERE value=:hash;", {'hash': hash})
        if self._curs.fetchone():
            logging.critical("hash of %s: %s" % (media_file.get_path(), hash))
            self._curs.execute("SELECT * FROM file_props;")
            file_props = self._curs.fetchone()
            filename = file_props[0]
            dirname = file_props[1]
            file_type = file_props[2]
            hash_value = file_props[3]

            filename2 = os.path.join(self._output_dir, dirname, filename)
            logging.critical("hash of %s: %s" % (filename2, hash_value))

            if not media_file.is_equal_to(filename2):
                logging.critical("MD5 hash collision for two different files,"
                                 "handled as dupe: %s %s", media_file.get_path(), filename2)

            logging.info("%s was detected as duplicate with %s" % (media_file.get_path(), filename2) )

            return True
        return False
