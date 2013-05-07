# vim: encoding: utf-8

from pyquery import PyQuery as pq

from . import utils

import itertools

import os

RELEASES_URL = 'http://download.enlightenment.org/releases/'

SRC_DL_DIR = os.path.join(os.path.expanduser('~'), 'src', 'e17')

def get_package_list(mirror):
    """Which packages are available in mirror?
    """

    packages = []

    url = pq(mirror)

    links = url('a')
    links = [pq(l) for l in links if utils.is_interesting(l)]
    links.sort(cmp=utils.pkg_name_sort)

    g = itertools.groupby(links, utils.name_from_link)

    for pkg, list_ in g:
        list_ = [l.attr('href') for l in list_]
        print pkg, list_
    
    # print [l.attr('href') for l in links]

    return packages

def main(args):
    """Tie all the pieces together to build e17
    """

    package_list = get_package_list(RELEASES_URL)

# EOF

