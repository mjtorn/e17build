#!/usr/bin/env python
# vim: fileencoding=utf-8

import os

import sys

from eb import e19b
from eb import utils

DEFAULTS = {
    'srcdir': os.path.join('/usr', 'src', 'e19'),
    'instpath': os.path.join('/opt', 'e19'),
    'thread_count': utils.get_thread_count()
}

# Why do I have to assign this manually?
__doc__ = """
E19 builder, run with sudo

Usage:
  e19build.py [--mirror=<url>] [--srcpath=<path>] [--instpath=<path>] [--thread-count=<n>] [--no-clean] [--rebuild] [--debug] [PACKAGE...]

Options:
  -m <url>, --mirror=<url>      Where to download from [default: http://download.enlightenment.org/]
  -s <path>, --srcpath=<path>   Where to download to [default: %(srcdir)s]
  -i <path>, --instpath=<path>  Where to install to [default: %(instpath)s]
  -t <n>, --thread-count=<n>    How many threads to (try to) use in compiling [default: %(thread_count)d]
  --no-clean                    Do not clean up old files
  --rebuild                     Rebuild sources, implies --no-clean
  --debug                       Build with -g -ggdb3
  PACKAGE                       Which package(s) to build. Must comply with rel/libs/elementary format

""" % DEFAULTS

from docopt import docopt

if __name__ == '__main__':
    args = docopt(__doc__)
    builder = e19b.E19Builder(args)
    sys.exit(builder.main(args))

# EOF

