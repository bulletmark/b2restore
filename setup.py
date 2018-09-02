#!/usr/bin/python3
# Setup script to install this package.
# M.Blakeney, Mar 2018.

import re, stat
from pathlib import Path
from setuptools import setup

here = Path(__file__).resolve().parent
name = re.sub(r'-.*', '', here.stem)
readme = here.joinpath('README.md').read_text()
executable = stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH

setup(
    name=name,
    version='1.9.2',
    description='Program to recreate Backblaze B2 file archive at'
            'specified date+time',
    long_description=readme,
    long_description_content_type='text/markdown',
    url='https://github.com/bulletmark/{}'.format(name),
    author='Mark Blakeney',
    author_email='mark@irsaere.net',
    keywords='backblaze b2',
    license='GPLv3',
    py_modules=[name],
    python_requires='>=3.5',
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
    data_files=[
        ('share/doc/{}'.format(name), ['README.md']),
    ],
    scripts=[f.name for f in here.iterdir()
        if f.is_file() and f.stat().st_mode & executable]
)
