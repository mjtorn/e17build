# vim: encoding: utf-8

from cStringIO import StringIO

from pyquery import PyQuery as pq

from .base import EnlightenmentBuilder

from . import utils

import itertools

import os

import tarfile

# These directories reflect the names of the packages
BUILD_ORDER = (
    # libs
    'rel/libs/efl', 'rel/libs/evas_generic_loaders', 'rel/libs/emotion_generic_players', 'rel/libs/elementary',
    'e_dbus',
    # apps
    'enlightenment', 'rel/apps/econnman', 'rel/apps/enventor', 'rel/apps/terminology',
    'etrophy', 'echievements', 'elemines',
    # bindings
    'rel/bindings/python',
)

class E17Builder(EnlightenmentBuilder):
    """Build e17
    """

    def __init__(self, args, build_order=BUILD_ORDER):
        """Set kwargs from this file
        """

        self.args = args
        self.build_order = BUILD_ORDER

    def get_package_dict(self, mirror):
        """Which packages are available in mirror?
        """

        print 'Getting from URL %s' % mirror

        packages = {}

        for pkg_path in self.build_order:
            # XXX: Maybe some day these will be moved to rel
            if not '/' in pkg_path:
                path = '/releases/'

                url = '%s%s' % (mirror, path)
                open_url = pq(url)

                links = open_url('a')
                links = [l for l in links if utils.is_interesting(l)]
                links = [l for l in links if pkg_path in l.attrib['href'] and not '0.18' in l.attrib['href']]
            else:
                path = pkg_path

                url = '%s%s' % (mirror, path)
                open_url = pq(url)

                links = open_url('a')
                links = [l for l in links if utils.is_interesting(l)]

            links = map(pq, links)
            assert len(links) > 0, 'Check your url: %s' % url
            links.sort(cmp=utils.pkg_name_sort)

            g = itertools.groupby(links, utils.name_from_link)

            for pkg, list_ in g:
                packages[pkg] = (path, [l.attr('href') for l in list_])

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
        for pkg, (path, pkg_versions) in packages.items():
            latest_pkg = pkg_versions[-1]
            url = '%s%s/%s' % (mirror, path, latest_pkg)
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

        print 'Packages: %s' % ', '.join(self.build_order)

        # TODO: Maybe store only the latest version in packages dict after download
        pkgs = [pkg.rsplit('/', 1)[-1] for pkg in self.build_order]
        for pkg in pkgs:
            pkg_path, pkg_list = packages[pkg]
            pkg_file = pkg_list[-1]
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

