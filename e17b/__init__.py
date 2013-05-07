# vim: encoding: utf-8

from cStringIO import StringIO

from pyquery import PyQuery as pq

from . import utils

import itertools

import os

import tarfile

RELEASES_URL = 'http://download.enlightenment.org/releases/'

SRC_DL_DIR = os.path.join(os.path.expanduser('~'), 'src', 'e17')

BUILD_ORDER = (
    'eina', 'eet', 'evas', 'evas_generic_loaders', 'ecore', 'eio', 'embryo',
    'edje', 'efreet', 'e_dbus', 'eeze', 'emotion', 'ethumb', 'elementary',
    'enlightenment',
)

BUILD_DST_DIR = os.path.join(os.path.expanduser('~'), 'e17build')

BUILD_THREAD_COUNT = utils.get_thread_count()

def get_package_dict(mirror):
    """Which packages are available in mirror?
    """

    packages = {}

    url = pq(mirror)

    links = url('a')
    links = [pq(l) for l in links if utils.is_interesting(l)]
    links.sort(cmp=utils.pkg_name_sort)

    g = itertools.groupby(links, utils.name_from_link)

    for pkg, list_ in g:
        packages[pkg] = [l.attr('href') for l in list_]

    # print [l.attr('href') for l in links]

    return packages

def download_packages(dst, mirror, packages, force_download=False):
    """Download from mirror
    Optionally force to download even if local file exists
    """

    # This could be smarter
    if not os.path.exists(dst):
        os.mkdir(dst)

    # Want to start building after download with multiprocessing...
    for pkg, pkg_versions in packages.items():
        latest_pkg = pkg_versions[-1]
        url = '%s%s' % (mirror, latest_pkg)
        print 'Downloading %s' % url

        dst_file = os.path.join(dst, latest_pkg)
        if not force_download and os.path.exists(dst_file):
            print 'File exists: %s' % dst_file
        else:
            utils.download(url, dst_file)

def build_packages(packages, dst, thread_count=BUILD_THREAD_COUNT):
    """Builder. Contains extraction too.
    """

    utils.remove_if_exists(BUILD_DST_DIR)
    os.mkdir(BUILD_DST_DIR)

    utils.setup_environment(BUILD_DST_DIR)

    # Maybe this should be smarter too :D
    for pkg in BUILD_ORDER:
        assert packages.has_key(pkg), '%s missing' % pkg

    print 'Packages: %s' % ', '.join(BUILD_ORDER)

    required_set = set(BUILD_ORDER)
    available_set = set(packages.keys())

    # Wouldn't it be nice to build these in parallell?
    extras = available_set.difference(required_set)
    print 'Extra packages: %s' % ', '.join(extras)

    # TODO: Maybe store only the latest version in packages dict after download
    for pkg in BUILD_ORDER + tuple(extras):
        pkg_file = packages[pkg][-1]
        path = os.path.join(dst, pkg_file)
        print path

        with tarfile.open(path) as tar:
            tar = tarfile.open(path)
            dst_dir = utils.verify_clean_build_dir(dst, tar)
            tar.extractall(path=dst, members=utils.safe_tar_files(tar, verbose=True))
            tar.close()

        build_package(dst_dir, BUILD_DST_DIR, thread_count=thread_count)

def build_package(src_dir, dst_dir, thread_count=BUILD_THREAD_COUNT):
    """Build source into destination
    """

    conf_cmd = ['./configure', '--prefix=%s' % dst_dir]
    make_cmd = ['make', '-j%d' % thread_count]
    install_cmd = ['make', 'install']

    utils.run(conf_cmd, src_dir)
    utils.run(make_cmd, src_dir)
    utils.run(install_cmd, src_dir)

def main(args):
    """Tie all the pieces together to build e17
    """

    package_dict = get_package_dict(RELEASES_URL)

    download_packages(SRC_DL_DIR, RELEASES_URL, package_dict)
    build_packages(package_dict, SRC_DL_DIR, thread_count=BUILD_THREAD_COUNT)

# EOF

