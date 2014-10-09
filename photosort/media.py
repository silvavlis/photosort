# -*- mode: python; coding: utf-8 -*-

__author__ = "Miguel Angel Ajo Pelayo"
__email__ = "miguelangel@ajo.es"
__copyright__ = "Copyright (C) 2013 Miguel Angel Ajo Pelayo"
__license__ = "GPLv3"

import filecmp
import hashlib
import logging
import os.path
import os
import stat
import sys
import datetime
import shutil
import glob

KnownSidecar = {'movie_with_metadata':
                        ['movie', 'photo'],
                'audio_with_metadata':
                        ['audio', 'photo']
                }

class MediaFile(object):

    def __init__(self, filename):
        self._filename = filename
        self._file_type = MediaFile.guess_file_type(filename)
        self._hash = None

    @staticmethod
    def guess_sidecar_file(filename):
        return MediaFile._guess_sidecar_file(filename)

    @staticmethod
    def _guess_sidecar_file(filename):
        media_group_files = glob.glob(os.path.splitext(filename)[0] + ".*")
        if len(media_group_files) < 2:
            return None
        elif len(media_group_files) == 2:
            logging.debug("Group of files found: %s" % str(media_group_files))
            for sidecar_format in KnownSidecar.keys():
                expected_files = list(KnownSidecar[sidecar_format])
                for index in [0, 1]:
                    file_type = MediaFile.guess_file_type(media_group_files[index])
                    if file_type in expected_files:
                        expected_files.remove(file_type)
                    else:
                        logging.debug("Files aren't '%s': %s" % 
                                (sidecar_format, str(media_group_files)))
                        break
                if not expected_files:
                    logging.debug("%s: %s" % 
                            (sidecar_format, str(media_group_files)))
                    return sidecar_format
        else:
            logging.error("Ignoring group of files: %s" % str(media_group_files))

    @staticmethod
    def guess_file_type(filename):
        extension = filename.lower().split('.')[-1]
        if extension in ('jpeg', 'jpg', 'png', 'thm', 'jpg_original', 'gif'):
            return 'photo'
        elif extension in ('cr2', 'raw', 'arw', 'orf', 'rw2', 'tif'):
            return 'raw'
        elif extension in ('mpeg', 'mpg', 'mov', 'mp4', 'avi', 'mts'):
            return 'movie'
        elif extension in ('wav'):
            return 'audio'
        return 'unknown'

    @staticmethod
    def build_for(filename):
        sidecar_type = MediaFile._guess_sidecar_file(filename)
        if sidecar_type:
            logging.info("Backpacked file '%s': %s" % 
                    (sidecar_type, os.path.splitext(filename)[0]))
            if sidecar_type is 'movie_with_metadata':
                import movierich    # delayed import to avoid circular dependencies
                return movierich.MovieRich(filename)
        else:
            file_type = MediaFile.guess_file_type(filename)
            logging.info("File is of type '%s': %s" % 
                    (file_type, filename))
            if file_type is 'photo':
                import photo    # delayed import to avoid circular dependencies
                return photo.Photo(filename)

        return MediaFile(filename)

    def get_filename(self):
        return os.path.basename(self._filename)

    def get_directory(self):
        return os.path.dirname(self._filename)

    def get_path(self):
        return self._filename

    def update_path(self, path):
        self._filename = path

    def hash(self, hasher=None, blocksize=65536):
        if self._hash is not None:
            return self._hash

        if hasher is None:
            hasher = hashlib.md5()

        with open(self._filename, 'rb') as afile:
            buf = afile.read(blocksize)
            while len(buf) > 0:
                hasher.update(buf)
                buf = afile.read(blocksize)

            self._hash = hasher.hexdigest()
            return self._hash

    def datetime(self):

        ct1 = os.path.getmtime(self._filename)
        ct2 = os.path.getctime(self._filename)

        ct = min(ct1,ct2) # it can differ from windows to UN*X

        return datetime.datetime.fromtimestamp(ct)

    def __str__(self):

        s = "[%s file hash=%s date=%s]" % (self._file_type, self.hash(), self.datetime())
        return s

    def is_equal_to(self,filename):

        try:
            result = filecmp.cmp(self._filename, filename, shallow=True)
            return result
        except OSError as e:

            logging.info("Comparing to %s, file didn't exist anymore, erased or moved?" % filename )
            return False

    def type(self):
        return self._file_type

    def makedirs_f(self, path, mode):
        paths = os.path.split(path)

        total_path = ''
        for directory in paths:
            total_path = os.path.join(total_path,directory)
            if os.path.isdir(total_path):
                continue
            else:
                os.mkdir(total_path,mode | stat.S_IXUSR)


    def rename_as(self,new_filename,file_mode = 0o774):

        try:
            self.makedirs_f(os.path.dirname(new_filename),file_mode)
        except:
            logging.error("Unable to move: %s" % new_filename)
            return False

        try:
            result = shutil.move(self._filename, new_filename)
            os.chmod(new_filename,file_mode)
        except OSError as e:
            logging.error("Unable to move: %s" % e)
            return False

        except IOError as e:
            logging.error("Unable to move: %s" % e)
            return False

        except shutil.Error as e:
            logging.error("Unable to move: %s" % e)
            return False

        except:
            raise

        return True

    def calculate_datetime(self,format):
        dt = self.datetime()
        data = {'year': dt.year, 'month': dt.month, 'day': dt.day,
                'hour': dt.hour, 'minute': dt.minute, 'second': dt.second }

        return format % data

    def move_to_directory_with_date(self,directory,dir_format,file_format='',file_mode=0o774):
        out_dir = directory + "/" + self.calculate_datetime(dir_format)

        try:
            os.mkdir(out_dir)
            os.chmod(out_dir,file_mode | stat.S_IXUSR)
        except OSError as e:
            pass # it already exists

        if file_format:
            file_prefix = self.calculate_datetime(file_format) + self.get_filename()
        else:
            file_prefix = self.get_filename()
        new_filename = out_dir + "/" + file_prefix
        logging.info("moving %s to %s" % (self._filename, new_filename))

        if self.rename_as(new_filename, file_mode):
            self.update_path(new_filename)
            return True
        else:
            return False

if __name__ == "__main__":
    file = MediaFile.build_for(sys.argv[1])
    print(file)

