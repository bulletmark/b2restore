## B2RESTORE

[b2restore](http://github.com/bulletmark/b2restore) is a command line
utility which can be used with [rclone](https://rclone.org/) to
manually restore a [Backblaze B2](https://www.backblaze.com/b2/) archive
for any given date and time. Alternatively, you can create a git
repository of all date and time snapshots (subject to the
[limitations](#limitations) described below).

### INSTALLATION

Arch users can install [b2restore from the
AUR](https://aur.archlinux.org/packages/b2restore/).

Python 3.6 or later is required. Note [b2restore is on
PyPI](https://pypi.org/project/b2restore/) so just ensure that
`python3-pip` and `python3-wheel` are installed then type the following
to install (or upgrade):

```
$ sudo pip3 install -U b2restore
```

Or, to install from this source repository:

```
$ git clone http://github.com/bulletmark/b2restore
$ cd b2restore
$ sudo pip3 install .
```

### CREATION OF INITIAL RCLONE COPY

This utility is typically used with [rclone](https://rclone.org/).
Simply `rclone sync` or `rclone copy` the B2 bucket or sub-paths from
the bucket which you want to restore. You **MUST** specify
`--b2-versions` to include all file versions, e.g:

```
rclone sync --b2-versions --fast-list --transfers=4 $* B2:mybucket b2files
```

The above command will copy all files and available versions to the
created `b2files` directory. You only need to do this once.

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
b2restore -t 2018-01-01T09:10.00 b2files outdir
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

You may wish to manually `git commit` each snapshot you create in the
outdir tree between your manually time-selected runs. If so, you will
need to add the `-g` switch to prevent `b2restore` from deleting your
top level `.git/` repo on each run.

Note that this utility does not recreate empty directory hierarchies.
All empty directories in the target tree are deleted.

### LIMITATIONS

If you want to restore a snapshot of your files for a specific
date/time, then unfortunately the metadata returned by
[rclone](https://rclone.org/) from [Backblaze
B2](https://www.backblaze.com/b2/) is not sufficient to create a
completely legitimate snapshot. However, all files restored for a
specific date/time will contain correct contents, the only issue is that
there may be some files which were actually deleted by that date but
those files may still be present. An example best illustrates the issue:

Say you run a rclone backup every night at 0000 am to B2:mybucket.

1. On 01-Jan you create a file `a.txt`.
2. On 02-Jan you delete file `a.txt`.
3. On 03-Jan you create file `a.txt` again (but with different content to 01-Jan).
4. On 04-Jan you retrieve the latest archive using `rclone sync
   --b2-versions --fast-list --transfers=4 $* B2:mybucket b2files`.

If you run `b2restore b2files outdir` then you will get the latest
03-Jan version of `a.txt` in `outdir`. If you then run `b2restore -t<time>
b2files outdir` for 01-Jan, then you will get `a.txt` with the correct
content from 01-Jan. However, if run that command for 02-Jan, then you
will still see the `a.txt` file and content corresponding to 01-Jan
(when it actually should be deleted for that day). If you are only using
b2restore to find and restore one or more files for specific date/times, then
this is not a serious practical problem. There may be some extra files
around, but all files are correct for the specified date/time.

#### B2RESTORE COMMAND LINE OPTIONS

```
usage: b2restore [-h] [-t TIME | -f FILETIME] [-s] [-g] [-p PATH]
                 indir [outdir]

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
  -s, --summary         just print a summary of files and versions
  -g, --gitkeep         preserve any top level git dir in outdir
  -p PATH, --path PATH  only process files under given path
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

#### B2RESTORE-CREATE-GIT COMMAND LINE OPTIONS

```
Usage: b2restore-create-git [-options] indir outdir
Create git repository from given B2 rclone copy.
Options:
-t YYYY-MM-DDTHH:MM.SS (start git repo from given time)
-e YYYY-MM-DDTHH:MM.SS (end git repo before given time)
-p (only process files under given path)
```

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
rclone lsl --b2-versions B2:mybucket | b2restore-create-dummy-files b2files
b2restore b2files outdir
du -shl outdir # (see how much storage tree of latest versions uses)
b2restore -t 2018-05-10T12:00.00 b2files outdir
du -shl outdir # (see how much storage tree of yesterdays versions uses)
```

#### B2RESTORE-CREATE-DUMMY-FILES COMMAND LINE OPTIONS

```
Usage: b2restore-create-dummy-files [-options] outdir
Reads B2 file list (from lsl output) from standard input to create
dummy tree of files.
Options:
-z (zero fill files, not with random content which is default)
-s (set files to zero length, not their actual size)
-p (only process files under given path)
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
