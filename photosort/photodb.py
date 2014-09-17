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
        self._output_dir = config.output_dir()
        self._file_mode = config.output_chmod()
        self._hashes = {}
        self._dbconn = None
        self._curs = None
        self.load()

    def load(self, merge=False, filename=None):
        """
        loads an existing DB

        If 'merge' is True, the values of previously loaded DBs (if any)
        are kept.
        If the path of a file is passed in 'filename', then
        """

        if filename is None:
            filename = self._db_file

        if not merge:
            self._hashes = {}

        if not os.path.isfile(filename):
            logging.info("no DB yet") 
            return

        logging.info("----------")
        logging.info("DB Loading %s" % filename)
        try:
            self._dbconn = sqlite3.connect(filename)
            self._dbconn.row_factory = sqlite3.Row
            self._curs = self._dbconn.cursor()
            self._curs.execute("SELECT * FROM file_props;")
            for row in self._curs:
                self._hashes[row['hash']] = {'dir': row['dir_name'],
                                          'name': row['file_name'],
                                          'type': row['file_type']}

            logging.info("DB Load finished, %d entries" % len(self._hashes))
        except:
            raise
        finally:
            self._curs.close()
            self._dbconn.close()

    def _create_schema(self):
        logging.debug("creating DB schema")

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
            '''CREATE VIEW file_props AS SELECT file.name AS file_name, 
                    directory.name AS dir_name, 
                    file_type.type AS file_type, hash.value AS hash FROM file 
                    INNER JOIN directory ON file.dir_id = directory.rowid 
                    INNER JOIN hash ON file.hash_id = hash.rowid 
                    INNER JOIN file_type ON file.type_id = file_type.rowid;'''
        ]

        for table_spec in tables:
            self._curs.execute(table_spec)
        for view_spec in views:
            self._curs.execute(view_spec)

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

    def write(self):
        db_empty = not os.path.isfile(self._db_file)

        self._dbconn = sqlite3.connect(self._db_file)
        self._curs = self._dbconn.cursor()
        if db_empty:
            self._create_schema()

        for hash in self._hashes.keys():
            hash_id = self._get_id_or_insert("hash", "value", hash)
            type_id = self._get_id_or_insert("file_type", "type", \
                    self._hashes[hash]['type'])
            dir_id = self._get_id_or_insert("directory", "name", \
                    self._hashes[hash]['dir'])
            self._curs.execute("INSERT INTO file(name, hash_id, type_id, " +
                    "dir_id) VALUES (:filename, :hash_id, :type_id, :dir_id);", \
                    {"filename": self._hashes[hash]['name'], \
                     "hash_id": hash_id, "type_id": type_id, "dir_id": dir_id})

        self._dbconn.commit()
        self._curs.close()
        self._dbconn.close()

    def add_to_db(self, file_dir, file_name, media_file):
        try:
            hash = media_file.hash()
        except IOError as e:
            logging.error("IOError %s trying to hash %s" %
                          (e,media_file.get_path()))
            return False

        file_type = media_file.type()

        # remove output dir path + '/'
        file_dir = file_dir[len(self._output_dir) + 1:]
        self._hashes[hash] = {'dir': file_dir,
                              'name': file_name,
                              'type': file_type}

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

        if hash in self._hashes:

            filename_data = self._hashes[hash]
            filename2 = self._output_dir + "/" + filename_data['dir']+'/'+filename_data['name']

            if not media_file.is_equal_to(filename2):
                logging.critical("MD5 hash collision for two different files,"
                                 "handled as dupe: %s %s", media_file.get_path(), filename2)

            logging.info("%s was detected as duplicate with %s" % (media_file.get_path(), filename2) )

            return True
        return False
