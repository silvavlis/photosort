# -*- mode: python; coding: utf-8 -*-
from __future__ import print_function

__author__ = "Silvano Cirujano Cuesta"
__email__ = "silvanociru@gmx.net"
__copyright__ = "Copyright (C) 2014 Silvano Cirujano Cuesta"
__license__ = "GPLv3"

import glob
import os.path
import media
import photo
import logging
import shutil

class MovieWithMetadata(media.MediaFile):

    def __init__(self, filename):
        media_group_files = glob.glob(os.path.splitext(filename)[0] + ".*")
        for filepath in media_group_files:
            if media.MediaFile.guess_file_type(filepath) == 'movie':
                media.MediaFile.__init__(self, filepath)
            elif media.MediaFile.guess_file_type(filepath) == 'photo':
                self._metadata = photo.Photo(filepath)
        self._file_type = 'movie_with_metadata'

    def datetime(self):
        return self._metadata.datetime()

    def rename_as(self,new_pack_path,file_mode=0o774):
        new_metadata_filename = new_pack_path + os.path.splitext(self._metadata._filename)[1]
        if not self._metadata.rename_as(new_metadata_filename, file_mode):
            return False

        new_movie_filename = new_pack_path + os.path.splitext(self._filename)[1]
        if not super(MovieWithMetadata, self).rename_as(new_movie_filename):
            return False

        return True

    def move_to_directory_with_date(self,directory,dir_format,file_format,file_mode=0o774):
        out_dir = directory + "/" + self.calculate_datetime(dir_format)

        try:
            os.mkdir(out_dir)
            os.chmod(out_dir,file_mode)
        except OSError as e:
            pass # it already exists

        new_pack_path = os.path.join(out_dir, self.calculate_datetime(file_format) + os.path.splitext(self.get_filename())[0])
        logging.info("'movie_with_metadata' -> moving %s to %s" % \
                (os.path.splitext(self._filename)[0], new_pack_path))

        if self.rename_as(new_pack_path):
            self._filename = new_pack_path + os.path.splitext(self._filename)[1]
            self._metadata._filename = new_pack_path + \
                    os.path.splitext(self._metadata._filename)[1]
            return True
        else:
            return False
