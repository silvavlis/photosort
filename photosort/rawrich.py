# -*- mode: python; coding: utf-8 -*-
from __future__ import print_function

__author__ = "Silvano Cirujano Cuesta"
__email__ = "silvanociru@gmx.net"
__copyright__ = "Copyright (C) 2014 Silvano Cirujano Cuesta"
__license__ = "GPLv3"

import glob
import os.path
from mediarich import MediaRich
import media
import photo

class RawRich(MediaRich):

    def __init__(self, filename):
        media_group_files = glob.glob(os.path.splitext(filename)[0] + ".*")
        for filepath in media_group_files:
            if media.MediaFile.guess_file_type(filepath) == 'raw':
                self.media = media.MediaFile(filepath)
            elif media.MediaFile.guess_file_type(filepath) == 'photo':
                self.metadata = photo.Photo(filepath)
        self._file_type = "raw_with_metadata"

