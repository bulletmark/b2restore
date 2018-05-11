#!/usr/bin/python3
# Setup script to install this package.
# M.Blakeney, Mar 2018.

import re
from pathlib import Path
from setuptools import setup

here = Path(__file__).resolve().parent
name = re.sub(r'-.*', '', here.stem)
readme = here.joinpath('README.md').read_text()

setup(
    name=name,
    version='1.0',
    description='Program to recreate Backblaze B2 file archive at'
            'specified date+time',
    long_description=readme,
    url=f'https://github.com/bulletmark/{name}',
    author='Mark Blakeney',
    author_email='mark@irsaere.net',
    classifiers=[
        'License :: OSI Approved :: GPL-3.0',
        'Programming Language :: Python :: 3',
    ],
    keywords='backblaze b2',
    py_modules=[name],
    data_files=[
        (f'share/doc/{name}', ['README.md']),
    ],
    scripts=[name],
)
