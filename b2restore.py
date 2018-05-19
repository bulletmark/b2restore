#!/usr/bin/python3
'Program to recreate Backblaze B2 file archive at specified date+time.'
# Author: Mark Blakeney, May 2018.

import sys, os, argparse, re, filecmp, time
from pathlib import Path
from bisect import bisect_left

TIMEFMT = '%Y-%m-%dT%H:%M.%S'

indir = None
outdir = None

class FileName():
    'Class to manage canonical file paths'
    namemap = {}

    def __init__(self, name):
        self.namemap[name] = self
        self.name = name
        self.times = []
        self.paths = []

    def add(self, path):
        'Insert the versioned file into list of sorted times'
        ix = bisect_left(self.times, path.time)
        self.times.insert(ix, path.time)
        self.paths.insert(ix, path)

class FileVersion():
    'Class to manage all versioned file paths'
    def __init__(self, path, subpath):
        self.path = subpath
        self.time = path.stat().st_mtime

        # Split B2 version file into name + version'
        pathstr = str(subpath)
        match = re.search(r'^(.+)-(v20\d{2}-\d{2}-\d{2}-\d{6}-\d{3})$', pathstr)
        self.name, self.version = \
                (match.group(1), match.group(2)) if match else (pathstr, None)

def parsefile(path):
    'Parse given file'
    subpath = path.relative_to(indir)
    fver = FileVersion(path, subpath)
    fname = FileName.namemap.get(fver.name)
    if not fname:
        fname = FileName(fver.name)

    # Add this file instance into the list of versions
    fname.add(fver)

def parsedir(dirpath, func):
    'Parse given dir and apply func() to files found'
    for f in dirpath.iterdir():
        if f.is_dir():
            parsedir(f, func)
        else:
            func(f)

# Keep valid file list
validfiles = set()

def addfile(fp, infile, outfile):
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

    date = time.strftime(TIMEFMT, time.localtime(fp.time))
    print('{} {}: {}'.format(action, date, fp.name))
    os.link(infile, outfile)

def delfile(path):
    'Delete given file if not needed anymore'
    ipath = path.relative_to(outdir)
    if str(ipath) not in validfiles:
        date = time.strftime(TIMEFMT, time.localtime(path.stat().st_mtime))
        print('deleting {}: {}'.format(date, ipath))
        path.unlink()

def main():
    'Main code'
    global indir, outdir

    # Process command line options
    opt = argparse.ArgumentParser(description=__doc__.strip())
    opt.add_argument('-t', '--time',
            help='set time YYYY-MM-DDTHH:MM.SS, default=latest')
    opt.add_argument('-f', '--filetime',
            help='set time based on specified file')
    opt.add_argument('indir',
            help='input B2 archive containing all file versions '
            ' (from --b2-versions)')
    opt.add_argument('outdir',
            help='output directory to recreate for given time')
    args = opt.parse_args()

    indir = Path(args.indir)
    outdir = Path(args.outdir)

    if args.filetime:
        afile = Path(args.filetime)
        if not afile.exists():
            opt.error('{} does not exist'.format(args.filetime))

        argstime = afile.stat().st_mtime
    elif args.time:
        argstime = time.mktime(time.strptime(args.time, TIMEFMT))
    else:
        argstime = None

    # Parse all files in the versioned indir
    parsedir(indir, parsefile)

    # Iterate through all files and restore version for given time
    outdir.mkdir(parents=True, exist_ok=True)
    for fname in FileName.namemap.values():
        ix = 0
        for i, tm in enumerate(fname.times):
            if argstime and tm > argstime:
                break
            ix += 1

        # Candidate files may all be newer than specified
        if ix == 0:
            continue

        fp = fname.paths[ix - 1]

        # If the latest version had a version string then this file must
        # have been deleted at this time
        if i == ix or not fp.version:
            addfile(fp, indir / fp.path, outdir / fname.name)

    # Delete any leftover files
    parsedir(outdir, delfile)

    # Delete all leftover empty dirs
    for root, dirs, files in os.walk(outdir, topdown=False):
        for name in dirs:
            dird = Path(root, name)
            if not any(dird.iterdir()) and dird != outdir:
                subdir = dird.relative_to(outdir)
                print('deleting empty {}'.format(subdir))
                dird.rmdir()

if __name__ == '__main__':
    sys.exit(main())
