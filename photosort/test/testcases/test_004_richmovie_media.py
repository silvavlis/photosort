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

class TestRichMovieMedia(photosort.test.TestCase):

    def setUp(self):
        self.m1mv = self.get_data_path('media3/mov1.mp4')
        self.m1sc = self.get_data_path('media3/mov1.jpg')
        self.m2mv = self.get_data_path('media3/mov2.mp4')
        self.m2sc = self.get_data_path('media3/mov2.jpg')
        self.m3mv = self.get_data_path('media3/mov3.mp4')
        self.m4sc = self.get_data_path('media3/mov4.jpg')
        self.m5mv = self.get_data_path('media3/mov5.mp4')
        self.m5sc = self.get_data_path('media3/mov5.jpg')
        self.m6mv = self.get_data_path('media3/mov6.mp4')
        self.m6sc = self.get_data_path('media3/mov6.jpg')
        self.m1mv_mtime = os.path.getmtime(self.m1mv)
        self.m1sc_mtime = os.path.getmtime(self.m1sc)
        self.richmovie1 = media.MediaFile.build_for(self.m1mv)
        self.richmovie2 = media.MediaFile.build_for(self.m1sc)
        
    def test_hash_creation(self):
        expected_hash = "d41d8cd98f00b204e9800998ecf8427e - 2013-08-24 13:05:52"
        self.assertEqual(self.richmovie1.hash(),expected_hash)
        self.assertEqual(self.richmovie2.hash(),expected_hash)

        # check for hasher non being re-started
        same_movie = media.MediaFile.build_for(self.m1mv)
        self.assertEqual(same_movie.hash(),expected_hash)

    def test_datetime(self):
        expected_datetime = "2013-08-24 13:05:52" # it must come from exif data
        self.assertEqual(str(self.richmovie1.datetime()),expected_datetime)
        self.assertEqual(str(self.richmovie2.datetime()),expected_datetime)

    def test_equal_checking(self):
        self.assertTrue(self.richmovie1.is_equal_to(self.m2mv))
        self.assertTrue(self.richmovie1.is_equal_to(self.m2sc))
        self.assertFalse(self.richmovie1.is_equal_to(self.m3mv))
        self.assertFalse(self.richmovie1.is_equal_to(self.m4sc))
        self.assertFalse(self.richmovie1.is_equal_to(self.m5mv))
        self.assertFalse(self.richmovie1.is_equal_to(self.m5sc))
        self.assertFalse(self.richmovie1.is_equal_to(self.m6mv))
        self.assertFalse(self.richmovie1.is_equal_to(self.m6sc))

    def test_datatime_dir(self):
        dir_fmt = '%(year)d/%(year)04d_%(month)02d_%(day)02d'
        dir_str = self.richmovie1.calculate_datetime(dir_fmt)
        self.assertEqual(dir_str,"2013/2013_08_24")
        dir_str = self.richmovie2.calculate_datetime(dir_fmt)
        self.assertEqual(dir_str,"2013/2013_08_24")

    def test_get_filename(self):
        self.assertEqual(self.richmovie1.get_filename(),'mov1.mp4')
        self.assertEqual(self.richmovie2.get_filename(),'mov1.mp4')

    def test_rename(self):
        tmpdir = tempfile.gettempdir()
        media_filename = self.richmovie1.media.get_filename()
        tmpmedia = os.path.join(tmpdir, media_filename)
        tmpmedia_renamed = os.path.join(tmpdir, 'R' + media_filename)
        metadata_filename = self.richmovie1.metadata.get_filename()
        tmpmetadata = os.path.join(tmpdir, metadata_filename)
        tmpmetadata_renamed = os.path.join(tmpdir, 'R' + metadata_filename)
        tmpfile_mode = 0o666

        shutil.copy(self.richmovie1.media.get_path(), tmpmedia)
        shutil.copy(self.richmovie1.metadata.get_path(), tmpmetadata)

        movie_t = media.MediaFile.build_for(tmpmedia)

        new_pack_path = os.path.splitext(tmpmedia_renamed)[0]
        movie_t.rename_as(new_pack_path,tmpfile_mode)
        result = self.richmovie1.is_equal_to(tmpmedia_renamed)
        self.assertTrue(self.richmovie1.is_equal_to(tmpmedia_renamed))

        file_mode = os.stat(tmpmedia_renamed)[stat.ST_MODE] & 0o777
        self.assertEqual(file_mode,tmpfile_mode)

    def test_move_to_directory(self):
        tmpdir = tempfile.gettempdir()
        tmpmedia = tmpdir + '/' + self.richmovie1.media.get_filename()
        tmpmetadata = tmpdir + '/' + self.richmovie1.metadata.get_filename()
        dir_fmt = '%(year)d/%(year)04d_%(month)02d_%(day)02d'
        file_fmt = '%(year)04d%(month)02d%(day)02d%(hour)02d%(minute)02d%(second)02d_'

        shutil.copy(self.richmovie1.media.get_path(), tmpmedia)
        shutil.copy(self.richmovie1.metadata.get_path(), tmpmetadata)
        richmovie_t = media.MediaFile.build_for(tmpmedia)

        shutil.rmtree(os.path.join(tmpdir, '2013'),ignore_errors=True)
        self.assertTrue(richmovie_t.move_to_directory_with_date(tmpdir,dir_fmt))

        expected_filename = os.path.join(tmpdir, '2013', '2013_08_24', 'mov1.mp4')
        self.assertEqual(expected_filename, richmovie_t.media.get_path())
        self.assertTrue(richmovie_t.is_equal_to(expected_filename))

        richmovie_t.move_to_directory_with_date(tmpdir,dir_fmt,file_fmt)
        expected_filename = os.path.join(tmpdir, '2013', '2013_08_24', '20130824130552_mov1.mp4')
        self.assertEqual(expected_filename, richmovie_t.media.get_path())
        self.assertTrue(self.richmovie1.is_equal_to(expected_filename))
        return




        mov_mtime = os.path.getmtime(tmpfile)
        mtime = time.localtime(mov_mtime)
        year = "%d" % mtime[0]
        month = "%02d" % mtime[1]
        day = "%02d" % mtime[2]
        hour = "%02d" % mtime[3]
        minute = "%02d" % mtime[4]
        second = "%02d" % mtime[5]
        movie_t = media.MediaFile.build_for(tmpfile)

        shutil.rmtree(tmpdir+'/'+year,ignore_errors=True)
        movie_t.move_to_directory_with_date(tmpdir,dir_fmt)

        expected_filename = os.path.join(tmpdir, year, year+'_'+month+'_'+day, 'mov1.mp4')
        self.assertTrue(self.movie.is_equal_to(expected_filename))

        shutil.copy(self.movie.get_path(), tmpfile)
        mov_mtime = os.path.getmtime(tmpfile)
        mtime = time.localtime(mov_mtime)
        year = "%d" % mtime[0]
        month = "%02d" % mtime[1]
        day = "%02d" % mtime[2]
        hour = "%02d" % mtime[3]
        minute = "%02d" % mtime[4]
        second = "%02d" % mtime[5]
        movie_t = media.MediaFile.build_for(tmpfile)

        shutil.rmtree(tmpdir+'/'+year,ignore_errors=True)
        movie_t.move_to_directory_with_date(tmpdir,dir_fmt,file_fmt)

        expected_filename = os.path.join(tmpdir, year, year+'_'+month+'_'+day, year+month+day+hour+minute+second+'_mov1.mp4')
        self.assertTrue(self.movie.is_equal_to(expected_filename))

if __name__ == '__main__':
    unittest.main()
   