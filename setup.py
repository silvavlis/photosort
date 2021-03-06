#!/usr/bin/env python

import setuptools

setuptools.setup(
        name = 'photosort',
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
        install_requires = ['pyaml', 'Pillow'],
        data_files = [('etc', ['etc/photosort.yml'])],
        test_suite = 'photosort.test.testcases'
        )



