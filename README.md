## B2RESTORE

[b2restore](http://github.com/bulletmark/b2restore) is a
command line utility which you can use to manually restore a Backblaze
B2 archive for a given date+time.

### INSTALLATION

Arch users can install [_b2restore from the
AUR_](https://aur.archlinux.org/packages/b2restore/).

Requires python 3.5+. Note [b2restore is on
PyPI](https://pypi.org/project/b2restore/) so you can `sudo pip install
b2restore` or:

```
$ git clone http://github.com/bulletmark/b2restore
$ sudo make install

```

### USAGE

Simply clone or copy the B2 bucket or sub paths which you want to restore
but ensure you specify `--b2-versions` to include all file versions,
e.g:

```
mkdir b2files
rclone sync --b2-versions --fast-list --transfers=4 $* B2:mybucket b2files
```

The run this utility to create a snapshot of the directory tree for the
file versions you are interested in.

E.g. to get the latest files:

```
b2restore b2files outdir
```

E.g. to get the files at a specified time:

```
b2restore -t 2018-01-01T09:10:00 b2files outdir
```

The utility prints a line for each file updated, created, or deleted
in outdir compared to the previous contents. The date+time of the file
is also listed.

```
usage: b2restore [-h] [-t TIME] [-f FILETIME] indir outdir

Program to recreate Backblaze B2 file archive at specified date+time.

positional arguments:
  indir                 input B2 archive containing all file versions (from
                        --b2-versions)
  outdir                output directory to recreate for given time

optional arguments:
  -h, --help            show this help message and exit
  -t TIME, --time TIME  set time YYYY-MM-DDTHH:MM.SS, default=latest
  -f FILETIME, --filetime FILETIME
                        set time based on specified file
```

### LICENSE

Copyright (C) 2018 Mark Blakeney. This program is distributed under the
terms of the GNU General Public License.
This program is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation, either version 3 of the License, or any later
version.
This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
Public License at <http://www.gnu.org/licenses/> for more details.

<!-- vim: se ai syn=markdown: -->
