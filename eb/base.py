# vim: fileencoding=utf-8

from collections import OrderedDict

from cStringIO import StringIO

from pyquery import PyQuery as pq

from . import utils

import itertools

import os

import tarfile

class EnlightenmentBuilder(object):
    """Extend this class for different enlightenment versions
    """

    def get_package_dict(self, mirror):
        """Which packages are available in mirror?
        """

        print 'Getting from URL %s' % mirror

        packages = OrderedDict()

        for pkg_path in self.build_order:
            # XXX: Maybe some day these will be moved to rel
            if not '/' in pkg_path:
                path = '/releases/'

                url = '%s%s' % (mirror, path)
                open_url = pq(url)

                links = open_url('a')
                links = [l for l in links if utils.is_interesting(l)]
                links = [l for l in links if pkg_path in l.attrib['href'] and not self.version in l.attrib['href']]
            else:
                path = pkg_path

                url = '%s%s' % (mirror, path)
                print '  %s' % url
                open_url = pq(url)

                links = open_url('a')
                # XXX: Another hack, this time to figure out the version
                if pkg_path == 'rel/apps/enlightenment':
                    links = [l for l in links if utils.is_interesting(l) and self.version in l.attrib['href']]
                else:
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

    def build_packages(self, packages, dst_base_path, instpath, thread_count=1, clean=True, rebuild=False, debug=False):
        """Builder. Contains extraction too.
        """

        print 'Attempt to build with thread count %d' % thread_count

        utils.remove_if_exists(instpath)
        # Hack around a potential symlink situation
        if not os.path.exists(instpath):
            os.mkdir(instpath)
        # And we need aclocal
        if not os.path.exists(os.path.join(instpath, 'share', 'aclocal')):
            os.mkdir(os.path.join(instpath, 'share'))
            os.mkdir(os.path.join(instpath, 'share', 'aclocal'))

        utils.setup_environment(instpath, debug=debug)

        print 'Packages: %s' % ', '.join(self.build_order)

        # TODO: Maybe store only the latest version in packages dict after download
        pkgs = [pkg.rsplit('/', 1)[-1] for pkg in self.build_order]
        for pkg in pkgs:
            # XXX: hate special case
            if pkg == 'python':
                pkg = 'python-efl'
            elif pkg == 'webkit-efl':
                pkg = 'ewebkit'

            try:
                pkg_path, pkg_list = packages[pkg]
            except KeyError:
                print packages.keys()
                raise
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

    def build_package(self, src_dir, dst_dir, thread_count=1, rebuild=False):
        """Build source into destination
        """

        ## XXX: The later additions mostly untested.
        # aclocal_cmd = ['aclocal']
        autogen_cmd = ['./autogen.sh', '--prefix=%s' % dst_dir]
        conf_cmd = ['./configure', '--prefix=%s' % dst_dir]
        make_cmd = ['make', '-j%d' % thread_count]
        install_cmd = ['make', 'install']
        setup_py_cmd = ['python', 'setup.py', 'install', '--prefix=%s/python/' % dst_dir]

        if os.path.exists(os.path.join(src_dir, 'setup.py')):
            utils.run(setup_py_cmd, src_dir)
        else:
            # XXX: Should be passed in from a conf section somewhere
            if '/efl-' in src_dir:
                # utils.run(aclocal_cmd, src_dir)
                autogen_cmd += ['--with-mount', '--with-umount']
                if os.path.exists('/bin/systemd'):
                    autogen_cmd.append('--enable-systemd')
            elif '/enlightement-' in src_dir:
                autogen_cmd += ['--enable-mount-eeze']
                if not os.path.exists('/bin/systemd'):
                    autogen_cmd.append('--disable-systemd')

            if os.path.exists(os.path.join(src_dir, 'autogen.sh')):
                utils.run(autogen_cmd, src_dir)
            elif os.path.exists(os.path.join(src_dir, 'configure')):
                utils.run(conf_cmd, src_dir)
            else:
                raise RuntimeError('Nothing found to do in %s' % src_dir)

            utils.run(make_cmd, src_dir)
            utils.run(install_cmd, src_dir)

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

        debug = args['--debug']

        # TODO: Do not assume new packages have been released
        # ie. populate package_dict with what's downloaded if rebuild is True
        self.download_packages(src_dir, mirror, package_dict)
        self.build_packages(package_dict, src_dir, instpath, thread_count=thread_count, clean=clean, rebuild=rebuild, debug=debug)

        print
        print 'DONE!'

        print
        print 'Remember to do the following:'
        print
        print 'sudo chown root:root %s/lib/enlightenment/modules/cpufreq/ARCH-VER/freqset' % instpath
        print 'sudo chmod u+s,a+x %s/lib/enlightenment/modules/cpufreq/ARCH-VER/freqset' % instpath
        print
        print 'sudo chown root:root %s/lib/enlightenment/utils/enlightenment_backlight' % instpath
        print 'sudo chmod u+s,a+x %s/lib/enlightenment/utils/enlightenment_backlight' % instpath
        print
        print 'sudo chown root:root %s/lib/enlightenment/utils/enlightenment_sys' % instpath
        print 'sudo chmod u+s,a+x %s/lib/enlightenment/utils/enlightenment_sys' % instpath
        print
        print 'sudo ln -s %s/share/dbus-1/services/* /usr/share/dbus-1/services/' % instpath


# EOF

