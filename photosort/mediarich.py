# -*- mode: python; coding: utf-8 -*-
from __future__ import print_function

__author__ = "Silvano Cirujano Cuesta"
__email__ = "silvanociru@gmx.net"
__copyright__ = "Copyright (C) 2014 Silvano Cirujano Cuesta"
__license__ = "GPLv3"

import os.path
import stat
import media
import logging
import shutil

class MediaRich(media.MediaFile):

    def __init__(self, filename):
        raise NotImplementedError, "No generic 'MediaRich', it should be 'MovieRich', 'RawRich'..."

    def datetime(self):
        return self.metadata.datetime()

    def get_path(self):
        raise NotImplementedError, "No path for 'MediaRich', either for media or for metadata"

    def get_filename(self):
        raise NotImplementedError, "No path for 'MediaRich', either for media or for metadata"

    def get_directory(self):
        raise NotImplementedError, "No path for 'MediaRich', either for media or for metadata"

    def update_path(self, filename):
        raise NotImplementedError, "No path for 'MediaRich', either for media or for metadata"

    def hash(self):
        media_hash = self.media.hash()
        exif_datetime = self.metadata.exif_datetime()

        if exif_datetime is not None:
            media_hash += " - " + str(exif_datetime)
        self._hash = media_hash
        return media_hash

    def is_equal_to(self,filename):
        sidecar_type = media.MediaFile.guess_sidecar_file(filename)
        if sidecar_type and (sidecar_type == self.type()):
            other_mediarich = media.MediaFile.build_for(filename)
            same_media = self.media.\
                    is_equal_to(other_mediarich.media.get_path())
            same_metadata = self.metadata.\
                    is_equal_to(other_mediarich.metadata.get_path())
            return same_media and same_metadata
        else:
            return False

    def rename_as(self,new_pack_path,file_mode=0o774):
        new_metadata_filename = new_pack_path + os.path.splitext(self.metadata.get_filename())[1]
        if not self.metadata.rename_as(new_metadata_filename, file_mode):
            return False

        new_media_filename = new_pack_path + os.path.splitext(self.media.get_path())[1]
        if not self.media.rename_as(new_media_filename, file_mode):
            return False

        return True

    def calculate_datetime(self,format):
        return self.metadata.calculate_datetime(format)

    def move_to_directory_with_date(self,directory,dir_format,file_format='',file_mode=0o774):
        out_dir = directory + "/" + self.calculate_datetime(dir_format)

        try:
            os.mkdir(out_dir)
            os.chmod(out_dir,file_mode | stat.S_IXUSR)
        except OSError as e:
            pass # it already exists

        if file_format:
            packname = os.path.join(self.calculate_datetime(file_format) + 
                    os.path.splitext(self.media.get_filename())[0])
        else:
            packname = os.path.splitext(self.media.get_filename())[0]
        new_pack_path = os.path.join(out_dir, packname)
        logging.info("'media_with_metadata' -> moving %s to %s" % \
                (os.path.splitext(self.media.get_path())[0], new_pack_path))

        if self.rename_as(new_pack_path, file_mode):
            self.media.update_path(new_pack_path + \
                    os.path.splitext(self.media.get_filename())[1])
            self.metadata.update_path(new_pack_path + \
                    os.path.splitext(self.metadata.get_filename())[1])
            return True
        else:
            return False
