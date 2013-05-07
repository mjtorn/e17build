# vim: encoding: utf-8

from pyquery import PyQuery as pq

import os

RELEASES_URL = 'http://download.enlightenment.org/releases/'

SRC_DL_DIR = os.path.join(os.path.expanduser('~'), 'src', 'e17')

def get_package_list(mirror):
    """Which packages are available in mirror?
    """

    packages = []

    url = pq(mirror)

    links = url('a')
    print links

    return packages

def main(args):
    """Tie all the pieces together to build e17
    """

    package_list = get_package_list(RELEASES_URL)

# EOF
