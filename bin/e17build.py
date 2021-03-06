#!/usr/bin/env python
# vim: fileencoding=utf-8

import os

import sys

from eb import e17b
from eb import utils

DEFAULTS = {
    'srcdir': os.path.join(os.path.expanduser('~'), 'src', 'e17'),
    'instpath': os.path.join(os.path.expanduser('~'), 'e17'),
    'thread_count': utils.get_thread_count()
}

# Why do I have to assign this manually?
__doc__ = """
E17 builder

Usage:
  e17build.py [--mirror=<url>] [--srcpath=<path>] [--instpath=<path>] [--thread-count=<n>] [--no-clean] [--rebuild]

Options:
  -m <url>, --mirror=<url>      Where to download from [default: http://download.enlightenment.org/]
  -s <path>, --srcpath=<path>   Where to download to [default: %(srcdir)s]
  -i <path>, --instpath=<path>  Where to install to [default: %(instpath)s]
  -t <n>, --thread-count=<n>    How many threads to (try to) use in compiling [default: %(thread_count)d]
  --no-clean                    Do not clean up old files
  --rebuild                     Rebuild sources, implies --no-clean

""" % DEFAULTS

from docopt import docopt

if __name__ == '__main__':
    args = docopt(__doc__)
    builder = e17b.E17Builder(args)
    sys.exit(builder.main(args))

# EOF

