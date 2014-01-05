# vim: encoding: utf-8

from cStringIO import StringIO

from pyquery import PyQuery as pq

from .base import EnlightenmentBuilder

from . import utils

import itertools

import os

import tarfile

BUILD_ORDER = (
    'eina', 'eet', 'evas', 'evas_generic_loaders', 'ecore', 'eio', 'embryo',
    'edje', 'efreet', 'e_dbus', 'eeze', 'emotion', 'ethumb', 'elementary',
    'enlightenment',
    # The order of these probably doesn't matter
    'python-evas', 'python-ecore', 'python-edje', 'python-e_dbus', 'python-emotion',
    'python-ethumb', 'python-elementary',
)

SKIP_BUILD = (
    'evil',
)

class E17Builder(EnlightenmentBuilder):
    """Build e17
    """

    def __init__(self, args, build_order=BUILD_ORDER, skip_build=SKIP_BUILD):
        """Set kwargs from this file
        """

        self.args = args
        self.build_order = BUILD_ORDER
        self.skip_build = SKIP_BUILD

    def get_package_dict(self, mirror, prepend=None):
        """Which packages are available in mirror?
        ``prepend`` eg. 'BINDINGS/python' (without slashes)
        """

        print 'Getting from URL %s' % mirror

        packages = {}

        url = pq(mirror)

        links = url('a')
        links = [pq(l) for l in links if utils.is_interesting(l) and not utils.is_ignored(l)]
        links.sort(cmp=utils.pkg_name_sort)

        g = itertools.groupby(links, utils.name_from_link)

        for pkg, list_ in g:
            packages[pkg] = [l.attr('href') for l in list_]
            if prepend is not None:
                packages[pkg] = ['/%s/%s' % (prepend, l) for l in packages[pkg]]

        # print [l.attr('href') for l in links]

        return packages

    def download_packages(self, dst, mirror, packages, force_download=False):
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

            latest_pkg = latest_pkg.rsplit('/', 1)[-1]
            dst_file = os.path.join(dst, latest_pkg)
            if not force_download and os.path.exists(dst_file):
                print 'File exists: %s' % dst_file
            else:
                utils.download(url, dst_file)

    def build_packages(self, packages, dst_base_path, instpath, thread_count=1, clean=True, rebuild=False):
        """Builder. Contains extraction too.
        """

        print 'Attempt to build with thread count %d' % thread_count

        utils.remove_if_exists(instpath)
        # Hack around a potential symlink situation
        if not os.path.exists(instpath):
            os.mkdir(instpath)

        utils.setup_environment(instpath)

        # Maybe this should be smarter too :D
        for pkg in self.build_order:
            assert packages.has_key(pkg), '%s missing' % pkg

        print 'Packages: %s' % ', '.join(self.build_order)

        required_set = set(self.build_order)
        available_set = set(packages.keys())

        # Wouldn't it be nice to build these in parallell?
        extras = available_set.difference(required_set)
        extras = list(extras)

        utils.dep_order(extras, 'etrophy', 'echievements')
        utils.dep_order(extras, 'etrophy', 'elemines')

        print 'Extra packages: %s' % ', '.join(extras)

        # TODO: Maybe store only the latest version in packages dict after download
        for pkg in self.build_order + tuple(extras):
            # TODO: This also needs to be saner, but now I got to get this crap finished
            if pkg in self.skip_build:
                print 'Skipping %s' % pkg
                continue

            pkg_file = packages[pkg][-1]
            pkg_file = pkg_file.rsplit('/', 1)[-1]
            path = os.path.join(dst_base_path, pkg_file)
            print path

            with tarfile.open(path) as tar:
                tar = tarfile.open(path)
                dst_dir = utils.verify_build_dir(dst_base_path, tar, clean=clean)
                if not rebuild:
                    tar.extractall(path=dst_base_path, members=utils.safe_tar_files(tar, verbose=True))
                tar.close()

            self.build_package(dst_dir, instpath, thread_count=thread_count, rebuild=rebuild)

    def main(self, args):
        """Tie all the pieces together to build e17
        """

        mirror = args['--mirror']
        if not mirror.startswith('http'):
            raise ValueError('Give http url to download from')

        src_dir = args['--srcpath']
        instpath = args['--instpath']

        thread_count = args['--thread-count']
        try:
            thread_count = int(thread_count)
        except ValueError:
            raise ValueError('Thread count must be integer')

        package_dict = self.get_package_dict(mirror)

        if not args['--no-python']:
            python_mirror = '%s/BINDINGS/python/' % args['--mirror']

            package_dict.update(self.get_package_dict(python_mirror, prepend='BINDINGS/python'))

        clean = not args['--no-clean']
        rebuild = args['--rebuild']

        if rebuild:
            clean = False

        # TODO: Do not assume new packages have been released
        # ie. populate package_dict with what's downloaded if rebuild is True
        self.download_packages(src_dir, mirror, package_dict)
        self.build_packages(package_dict, src_dir, instpath, thread_count=thread_count, clean=clean, rebuild=rebuild)

        print
        print 'DONE!'

        print
        print '(Remember to chown root and chmod u+s,a+x the freqset executable)'

# EOF

