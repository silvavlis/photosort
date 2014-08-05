# -*- mode: python; coding: utf-8 -*-
from __future__ import print_function

__author__ = "Silvano Cirujano Cuesta"
__email__ = "silvanociru@gmx.net"
__copyright__ = "Copyright (C) 2014 Silvano Cirujano Cuesta"
__license__ = "GPLv3"

import glob
import os.path
from media_with_metadata import MediaWithMetadata
import media
import photo

class RawWithMetadata(MediaWithMetadata):

    def __init__(self, filename):
        media_group_files = glob.glob(os.path.splitext(filename)[0] + ".*")
        for filepath in media_group_files:
            if media.MediaFile.guess_file_type(filepath) == 'raw':
                media.MediaFile.__init__(self, filepath)
            elif media.MediaFile.guess_file_type(filepath) == 'photo':
                self._metadata = photo.Photo(filepath)

