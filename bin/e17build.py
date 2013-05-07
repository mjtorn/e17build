#!/usr/bin/env python
# vim: encoding=utf-8

import os

import sys

import e17b

DEFAULTS = {
    'srcdir': os.path.join(os.path.expanduser('~'), 'src', 'e17'),
    'instpath': os.path.join(os.path.expanduser('~'), 'e17'),
    'thread_count': e17b.utils.get_thread_count()
}

# Why do I have to assign this manually?
__doc__ = """
E17 builder

Usage:
  e17build.py [--mirror=<url>] [--srcpath=<path>] [--instpath=<path>] [--thread-count=<n>]

Options:
  -m <url>, --mirror=<url>      Where to download from [default: http://download.enlightenment.org/releases/]
  -s <path>, --srcpath=<path>   Where to download to [default: %(srcdir)s]
  -i <path>, --instpath=<path>  Where to install to [default: %(instpath)s]
  -t <n>, --thread-count=<n>    How many threads to (try to) use in compiling [default: %(thread_count)d]

""" % DEFAULTS

from docopt import docopt

if __name__ == '__main__':
    args = docopt(__doc__)
    sys.exit(e17b.main(args))

# EOF
