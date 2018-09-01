## B2RESTORE

[b2restore](http://github.com/bulletmark/b2restore) is a command line
utility which can be used with [rclone](https://rclone.org/) to
manually restore a [Backblaze B2](https://www.backblaze.com/b2/) archive
for any given date and time. Alternatively, you can create a git
repository of all date and time snapshots.

### INSTALLATION

Arch users can install [b2restore from the
AUR](https://aur.archlinux.org/packages/b2restore/).

Requires python 3.5 or later. Note [b2restore is on
PyPI](https://pypi.org/project/b2restore/) so you can `sudo pip install
b2restore` or:

```
$ git clone http://github.com/bulletmark/b2restore
$ sudo make install
```

### CREATION OF INITIAL RCLONE COPY

This utility is typically used with [rclone](https://rclone.org/).
Simply `rclone sync` or `rclone copy` the B2 bucket or sub-paths from
the bucket which you want to restore. You **MUST** specify
`--b2-versions` to include all file versions, e.g:

```
mkdir b2files
rclone sync --b2-versions --fast-list --transfers=4 $* B2:mybucket b2files
```

The above command will copy all files and available versions to the
`b2files` directory. You only need to do this once.

### CREATION OF SNAPSHOT AT GIVEN TIME

Given the above `rclone` initial copy, you run this utility to
create a snapshot of the directory tree for the time you are interested
in.

E.g. to recreate the tree of latest files, in `outdir`:

```
b2restore b2files outdir
```

E.g. to recreate the tree of files at a specified time:

```
b2restore -t 2018-01-01T09:10:00 b2files outdir
```

Just keep selecting different times to incrementally recreate `outdir`
as it existed at that time. The utility prints a line for each file
updated, created, or deleted in `outdir` compared to the previous
contents. The date and time of each updated/created/deleted file is also
listed. The target files are all hard-linked from the files in the
source directory so the `outdir` tree is created very quickly since
files do not need to be actually copied. Thus you can conveniently
experiment with the time string to quickly see file differences.

Rather than specifying an explicit time string using `-t/--time`, you
can instead choose to use `-f/--filetime` to specify any one specific
file's modification time at which to recreate the target tree of files.

Note that this utility does not recreate empty directory hierarchies.
All empty directories in the target tree are deleted.

#### B2RESTORE COMMAND LINE OPTIONS

```
usage: b2restore [-h] [-t TIME | -f FILETIME] indir outdir

Program to recreate Backblaze B2 file archive at specified date and time.

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

### CREATION OF GIT REPOSITORY OF ALL SNAPSHOTS

Rather than run `b2restore` for the given date + times you are
interested in, you can instead choose to run the provided
`b2restore-create-git` utility to automatically create a git repository
of snapshots of files for all the dates + times inherent in the `rclone`
initial copy.

So after performing the `rclone` initial copy above, run the following
command to create a complete git repository:

```
b2restore-create-git b2files outdir
```

Then `cd outdir` and run `git log` etc to view the history.

The utility `b2restore-create-git` takes no optional command line
arguments.

### TEST RUN UTILITY

A command line utility `b2restore-create-dummy-files` is included to
facilitate testing `b2restore` on your restored file tree without
actually downloading any files from your B2 archive(!). This utility
parses `rclone lsl` output to recreate your B2 bucket directory and
hierarchy of file versions. Only the file names are recreated of course,
the file contents are set to their actual byte size but with random byte
contents (or zero filled if you specify `-z`, or to zero length if you
specify `-s`).

This utility requires almost nothing to download from your B2 archive
and runs extremely quickly. You can then run `b2restore` against this
dummy archive to simulate what files are changed between versions, etc.
It is also good to get a feel for how `b2restore` works, what it does,
and whether it suits your needs without requiring you to first perform
an onerous huge download of your entire B2 archive.

Here is an example usage:

```
rclone lsl --b2-versions B2:mybucket | b2restore-create-dummy-files -d allfiles
b2restore allfiles b2
du -shl b2 # (see how much storage tree of latest versions uses)
b2restore -t 2018-05-10T12:00.00 allfiles b2
du -shl b2 # (see how much storage tree of yesterdays versions uses)
```

#### B2RESTORE-CREATE-DUMMY-FILES COMMAND LINE OPTIONS

```
Usage: b2restore-create-dummy-files [-options]
Reads B2 file list (from lsl output) from standard input to create
dummy tree of files.
Options:
-d <outdir> default = current dir
-z (zero fill files, not with random content which is default)
-s (set files to zero length, not their actual size)
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
