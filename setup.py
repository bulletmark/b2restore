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
    version='1.4',
    description='Program to recreate Backblaze B2 file archive at'
            'specified date+time',
    long_description=readme,
    long_description_content_type="text/markdown",
    url=f'https://github.com/bulletmark/{name}',
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
        (f'share/doc/{name}', ['README.md']),
    ],
    scripts=[name],
)
