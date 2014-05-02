#!/usr/bin/env python

import setuptools
import sys

exif_reader = ''
supported_exif_readers = ['PIL', 'exifread']

if sys.argv[-1] in supported_exif_readers:
    exif_reader = sys.argv.pop()
else:
    exif_reader = 'PIL'

tool_name = 'photosort'
if exif_reader != 'PIL':
    tool_name = tool_name + '-' + exif_reader

setuptools.setup(
        name = tool_name,
        version = '2014.1a',
        description = 'Picture inbox simplified',
        author = 'Miguel Angel Ajo Pelayo',
        author_email = 'miguelangel@ajo.es',
        url = 'https://github.com/mangelajo/photosort',
        packages = setuptools.find_packages(exclude = ['ez_setup']),
        include_package_data = True,
        zip_safe = False,
        entry_points = {
            'console_scripts': [
                'photosort = photosort.photosort:main'
            ]},
        install_requires = ['pyaml', exif_reader],
        data_files = [('etc', ['etc/photosort.yml'])],
        test_suite = 'photosort.test.testcases'
        )



