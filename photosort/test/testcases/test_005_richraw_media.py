# -*- mode: python; coding: utf-8 -*-

__author__ = "Miguel Angel Ajo Pelayo"
__email__ = "miguelangel@ajo.es"
__copyright__ = "Copyright (C) 2013 Miguel Angel Ajo Pelayo"
__license__ = "GPLv3"

import photosort.test
from photosort import media
import shutil
import tempfile
import os
import stat
import time

class TestRichRawMedia(photosort.test.TestCase):

    def setUp(self):
        self.m1rw = self.get_data_path('media4/raw1.arw')
        self.m1sc = self.get_data_path('media4/raw1.jpg')
        self.m2rw = self.get_data_path('media4/raw2.arw')
        self.m2sc = self.get_data_path('media4/raw2.jpg')
        self.m3rw = self.get_data_path('media4/raw3.arw')
        self.m4sc = self.get_data_path('media4/raw4.jpg')
        self.m5rw = self.get_data_path('media4/raw5.arw')
        self.m5sc = self.get_data_path('media4/raw5.jpg')
        self.m6rw = self.get_data_path('media4/raw6.arw')
        self.m6sc = self.get_data_path('media4/raw6.jpg')
        self.m1rw_mtime = os.path.getmtime(self.m1rw)
        self.m1sc_mtime = os.path.getmtime(self.m1sc)
        self.richraw1 = media.MediaFile.build_for(self.m1rw)
        self.richraw2 = media.MediaFile.build_for(self.m1sc)
        
    def test_hash_creation(self):
        expected_hash = "d41d8cd98f00b204e9800998ecf8427e - 2013-08-24 13:05:52"
        self.assertEqual(self.richraw1.hash(),expected_hash)
        self.assertEqual(self.richraw2.hash(),expected_hash)

        # check for hasher non being re-started
        same_raw = media.MediaFile.build_for(self.m1rw)
        self.assertEqual(same_raw.hash(),expected_hash)

    def test_datetime(self):
        expected_datetime = "2013-08-24 13:05:52" # it must come from exif data
        self.assertEqual(str(self.richraw1.datetime()),expected_datetime)
        self.assertEqual(str(self.richraw2.datetime()),expected_datetime)

    def test_equal_checking(self):
        self.assertTrue(self.richraw1.is_equal_to(self.m2rw))
        self.assertTrue(self.richraw1.is_equal_to(self.m2sc))
        self.assertFalse(self.richraw1.is_equal_to(self.m3rw))
        self.assertFalse(self.richraw1.is_equal_to(self.m4sc))
        self.assertFalse(self.richraw1.is_equal_to(self.m5rw))
        self.assertFalse(self.richraw1.is_equal_to(self.m5sc))
        self.assertFalse(self.richraw1.is_equal_to(self.m6rw))
        self.assertFalse(self.richraw1.is_equal_to(self.m6sc))

    def test_datetime_dir(self):
        dir_fmt = '%(year)d/%(year)04d_%(month)02d_%(day)02d'
        dir_str = self.richraw1.calculate_datetime(dir_fmt)
        self.assertEqual(dir_str,"2013/2013_08_24")
        dir_str = self.richraw2.calculate_datetime(dir_fmt)
        self.assertEqual(dir_str,"2013/2013_08_24")

    def test_get_filename(self):
        self.assertEqual(self.richraw1.media.get_filename(),'raw1.arw')
        self.assertEqual(self.richraw2.metadata.get_filename(),'raw1.jpg')
        self.assertEqual(self.richraw1.get_filename(),'raw1.arw')

    def test_rename(self):
        tmpdir = tempfile.gettempdir()
        media_filename = self.richraw1.media.get_filename()
        tmpmedia = os.path.join(tmpdir, media_filename)
        tmpmedia_renamed = os.path.join(tmpdir, 'R' + media_filename)
        metadata_filename = self.richraw1.metadata.get_filename()
        tmpmetadata = os.path.join(tmpdir, metadata_filename)
        tmpmetadata_renamed = os.path.join(tmpdir, 'R' + metadata_filename)
        tmpfile_mode = 0o666

        shutil.copy(self.richraw1.media.get_path(), tmpmedia)
        shutil.copy(self.richraw1.metadata.get_path(), tmpmetadata)

        raw_t = media.MediaFile.build_for(tmpmedia)

        new_pack_path = os.path.splitext(tmpmedia_renamed)[0]
        raw_t.rename_as(new_pack_path,tmpfile_mode)
        result = self.richraw1.is_equal_to(tmpmedia_renamed)
        self.assertTrue(self.richraw1.is_equal_to(tmpmedia_renamed))

        file_mode = os.stat(tmpmedia_renamed)[stat.ST_MODE] & 0o777
        self.assertEqual(file_mode,tmpfile_mode)

    def test_move_to_directory(self):
        tmpdir = tempfile.gettempdir()
        tmpmedia = tmpdir + '/' + self.richraw1.media.get_filename()
        tmpmetadata = tmpdir + '/' + self.richraw1.metadata.get_filename()
        dir_fmt = '%(year)d/%(year)04d_%(month)02d_%(day)02d'
        file_fmt = '%(year)04d%(month)02d%(day)02d%(hour)02d%(minute)02d%(second)02d_'

        shutil.copy(self.richraw1.media.get_path(), tmpmedia)
        shutil.copy(self.richraw1.metadata.get_path(), tmpmetadata)
        richraw_t = media.MediaFile.build_for(tmpmedia)

        shutil.rmtree(os.path.join(tmpdir, '2013'),ignore_errors=True)
        self.assertTrue(richraw_t.move_to_directory_with_date(tmpdir,dir_fmt))

        expected_filename = os.path.join(tmpdir, '2013', '2013_08_24', 'raw1.arw')
        self.assertEqual(expected_filename, richraw_t.media.get_path())
        self.assertTrue(richraw_t.is_equal_to(expected_filename))

        richraw_t.move_to_directory_with_date(tmpdir,dir_fmt,file_fmt)
        expected_filename = os.path.join(tmpdir, '2013', '2013_08_24', '20130824130552_raw1.arw')
        self.assertEqual(expected_filename, richraw_t.media.get_path())
        self.assertTrue(self.richraw1.is_equal_to(expected_filename))

if __name__ == '__main__':
    unittest.main()
   
