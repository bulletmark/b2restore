#!/usr/bin/python3
'Program to recreate Backblaze B2 file archive at specified date and time.'
# Author: Mark Blakeney, May 2018.

import argparse
import filecmp
import os
import re
import time
from bisect import bisect
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Callable

# Format of input and output datetimes
TIMEFMT = '%Y-%m-%dT%H:%M.%S'

indir = None
outdir = None
exgit = []
args = None

class FileVersion:
    'Class to manage all versioned file paths'
    def __init__(self, path: Path, subpath: Path):
        stat = path.stat()
        self.path = subpath
        self.size = stat.st_size
        self.name = str(subpath)
        self.time = datetime.fromtimestamp(stat.st_mtime)
        self.version = None

        # Find B2 version string in file name. I will admit I don't
        # understand the logic of where they embed the version string so
        # this is crude.
        match = re.search(r'^(.+)-v(20\d{2}-\d{2}-\d{2}-\d{6}-\d{3})(.*)$',
                self.name)
        if not match:
            return

        timestr = match.group(2) + '000'

        # Ensure we did actually find a valid datetime string
        try:
            fver = datetime.strptime(timestr, '%Y-%m-%d-%H%M%S-%f')
        except ValueError:
            return

        self.name = match.group(1) + match.group(3)

        # Timezone is in UTC. Convert to local (naive) time.
        fver = fver.replace(tzinfo=timezone.utc)
        self.version = fver.astimezone().replace(tzinfo=None)

class FileName:
    'Class to manage canonical file paths'
    namemap = {}

    def __init__(self, name: str):
        self.namemap[name] = self
        self.name = name
        self.times = []
        self.paths = []

    def add(self, fver: FileVersion) -> None:
        'Insert the versioned file into list of sorted times'
        ix = bisect(self.times, fver.time)
        if ix > 0:
            opath = self.paths[ix - 1]
            # If this file looks to be the same as another then prefer
            # the non-versioned file
            if opath.time == fver.time:
                if opath.version and not fver.version:
                    self.paths[ix - 1] = fver
                return

        self.times.insert(ix, fver.time)
        self.paths.insert(ix, fver)

def parsefile(path: Path) -> None:
    'Parse given file'
    subpath = path.relative_to(indir)  # type: ignore
    if args.path and not str(subpath).startswith(args.path):  # type:ignore
        return

    fver = FileVersion(path, subpath)
    fname = FileName.namemap.get(fver.name)
    if not fname:
        fname = FileName(fver.name)

    # Add this file instance into the list of versions
    fname.add(fver)

def parsedir(dirpath: Path, func: Callable[[Path], None]) -> None:
    'Parse given dir and apply func() to files found'
    for f in dirpath.iterdir():
        if f.is_dir():
            parsedir(f, func)
        else:
            func(f)

# Keep valid file list
validfiles = set()

def fmttime(dtime: datetime) -> str:
    'Return string rep of given time'
    return dtime.strftime(TIMEFMT)

def addfile(fp: FileVersion, infile: Path, outfile: Path) -> None:
    'Copy infile to outfile if changed'
    validfiles.add(fp.name)
    if outfile.exists():
        if filecmp.cmp(infile, outfile):
            return
        outfile.unlink()
        action = 'updating'
    else:
        action = 'creating'
        outfile.parent.mkdir(parents=True, exist_ok=True)

    print(f'{action} {fmttime(fp.time)}: {fp.name}')
    os.link(infile, outfile)

def delfile(path: Path) -> None:
    'Delete given file if not needed anymore'
    ipath = path.relative_to(outdir)  # type: ignore
    if ipath.parts[0] in exgit:
        return
    if str(ipath) not in validfiles:
        vers = fmttime(datetime.fromtimestamp(path.stat().st_mtime))
        print(f'deleting {vers}: {ipath}')
        path.unlink()

def main() -> None:
    'Main code'
    global indir, outdir, args

    # Process command line options
    opt = argparse.ArgumentParser(description=__doc__)
    grp = opt.add_mutually_exclusive_group()
    grp.add_argument('-t', '--time',
            help='set time YYYY-MM-DD[THH:MM[.SS]], default=latest')
    grp.add_argument('-f', '--filetime',
            help='set time based on specified file')
    opt.add_argument('-s', '--summary', action='store_true',
            help='just print a summary of files and versions')
    opt.add_argument('-g', '--gitkeep', action='store_true',
            help='preserve any top level git dir in outdir')
    opt.add_argument('-p', '--path',
            help='only process files under given path')
    opt.add_argument('indir',
            help='input B2 archive containing all file versions '
            ' (from --b2-versions)')
    opt.add_argument('outdir', nargs='?',
            help='output directory to recreate for given time')
    args = opt.parse_args()

    indir = Path(args.indir).expanduser()

    if not indir.is_dir():
        opt.error('indir must be a directory')

    if not args.summary:
        if not args.outdir:
            opt.error('outdir must be specified')

        outdir = Path(args.outdir).expanduser()

        if outdir.exists():
            if not outdir.is_dir():
                opt.error('outdir must be a directory')

            if args.gitkeep:
                exgit.extend([str(d) for d in outdir.glob('.git*')])

        outdir.mkdir(parents=True, exist_ok=True)

        if indir.stat().st_dev != outdir.stat().st_dev:
            opt.error('indir and outdir must on same file system')

    if args.filetime:
        afile = Path(args.filetime)
        if not afile.exists():
            opt.error(f'{args.filetime} does not exist')

        argstime = datetime.fromtimestamp(afile.stat().st_mtime)
    elif args.time:
        # Allow user to just specify date or just date + hhmm

        if len(args.time) == 10:
            args.time += 'T23:59.59'
        elif len(args.time) == 16:
            args.time += '.59'

        if args.time[10] == ' ':
            args.time = args.time[:10] + 'T' + args.time[11:]

        argstime = datetime.strptime(args.time, TIMEFMT)

        # Add a large fraction to ensure we match against file times which
        # include msecs.
        argstime += timedelta(
                seconds=(1 - time.clock_getres(time.CLOCK_MONOTONIC)))
    else:
        argstime = None

    # Parse all files in the versioned indir
    parsedir(indir, parsefile)  # type:ignore

    if args.summary:
        fnames = sorted(FileName.namemap)
        for fname in fnames:
            print(f'{fname}:')
            for fpath in FileName.namemap[fname].paths:
                vers = fmttime(fpath.version) if fpath.version \
                        else '----- current -----'
                print(f'  {fmttime(fpath.time)} {vers} {fpath.size:8} B')
        return

    # Iterate through all files and restore version for given time
    for fname in FileName.namemap.values():
        index = 0
        for index, tm in enumerate(fname.times):
            if argstime and tm > argstime:
                break
        else:
            index += 1

        # Candidate files may all be newer than specified
        if index == 0:
            continue

        fp = fname.paths[index - 1]

        # If the latest version had a version string then this file may
        # have been deleted at this time
        if index < len(fname.times) or not fp.version or \
                (argstime and argstime <= fp.version):
            addfile(fp, indir / fp.path, outdir / fname.name)

    # Delete any leftover files
    parsedir(outdir, delfile)  # type:ignore

    # Delete all leftover empty dirs
    for root, dirs, files in os.walk(outdir, topdown=False):  # type:ignore
        for name in dirs:
            dird = Path(root, name)  # type: ignore
            if dird.parts[0] not in exgit:
                if not any(dird.iterdir()) and dird != outdir:
                    print('deleting empty '
                          f'{dird.relative_to(outdir)}')  # type: ignore
                    dird.rmdir()

if __name__ == '__main__':
    main()
