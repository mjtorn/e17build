# vim: encoding: utf-8

from cStringIO import StringIO

from pyquery import PyQuery as pq

from . import utils

import git

import itertools

import os

import tarfile

BUILD_ORDER = (
    'eina', 'eet', 'evas', 'evas_generic_loaders', 'ecore', 'eio', 'embryo',
    'edje', 'efreet', 'e_dbus', 'eeze', 'emotion', 'ethumb', 'elementary',
    'enlightenment',
)

SKIP_BUILD = (
    'evil',
)

GIT_PATHS = {
    'econnman': 'git://git.enlightenment.org/apps/econnman.git',
    'python-efl': 'git://git.enlightenment.org/bindings/python/python-efl.git',
    'efl': 'git://git.enlightenment.org/core/efl.git',
}

def get_package_dict(mirror):
    """Which packages are available in mirror?
    """

    print 'Getting from URL %s' % mirror

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

def download_git(dst, git_packages, packages):
    """Check out git
    """

    if not os.path.exists(dst):
        os.mkdir(dst)

    for pkg, to_install in git_packages.items():
        if not to_install:
            continue

        dst_path = os.path.join(dst, pkg)
        if not os.path.exists(dst_path):
            #os.mkdir(dst_path)

            ## This does not appear to work
            #repo = git.Repo(GIT_PATHS[pkg])
            #repo.clone(dst_path)
            git_repo = GIT_PATHS[pkg]
            print 'Cloning %s into %s' % (GIT_PATHS[pkg], dst_path)

            git.Git().clone(GIT_PATHS[pkg], dst_path)
        else:
            print 'Updating repo at %s' % dst_path
            repo = git.Repo(dst_path)

            repo.remotes.origin.pull()

        # Look like a list of versions for later
        packages[pkg] = [dst_path]

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

def build_packages(packages, dst_base_path, instpath, thread_count=1):
    """Builder. Contains extraction too.
    """

    print 'Attempt to build with thread count %d' % thread_count

    utils.remove_if_exists(instpath)
    os.mkdir(instpath)

    utils.setup_environment(instpath)

    # Maybe this should be smarter too :D
    for pkg in BUILD_ORDER:
        assert packages.has_key(pkg), '%s missing' % pkg

    print 'Packages: %s' % ', '.join(BUILD_ORDER)

    required_set = set(BUILD_ORDER)
    available_set = set(packages.keys())

    # Wouldn't it be nice to build these in parallell?
    extras = available_set.difference(required_set)
    extras = list(extras)

    # TODO: Maybe model extra package deps somewhere?
    utils.dep_order(extras, 'etrophy', 'echievements')
    if 'econnman' in extras:
        utils.dep_order(extras, 'python-efl', 'econnman')
    if 'python-efl' in extras:
        utils.dep_order(extras, 'efl', 'python-efl')

    print 'Extra packages: %s' % ', '.join(extras)

    # TODO: Maybe store only the latest version in packages dict after download
    for pkg in BUILD_ORDER + tuple(extras):
        # TODO: This also needs to be saner, but now I got to get this crap finished
        if pkg in SKIP_BUILD:
            print 'Skipping %s' % pkg
            continue

        pkg_file = packages[pkg][-1]
        path = os.path.join(dst_base_path, pkg_file)
        print path

        # Deal different with tarballs and git clones
        if os.path.isfile(path):
            with tarfile.open(path) as tar:
                tar = tarfile.open(path)
                dst_dir = utils.verify_clean_build_dir(dst_base_path, tar)
                tar.extractall(path=dst_base_path, members=utils.safe_tar_files(tar, verbose=True))
                tar.close()
        else:
            dst_dir = path

        build_package(dst_dir, instpath, thread_count=thread_count)

def build_package(src_dir, dst_dir, thread_count=1):
    """Build source into destination
    """

    ## XXX: The later additions mostly untested.
    autogen_cmd = ['./autogen.sh']
    conf_cmd = ['./configure', '--prefix=%s' % dst_dir]
    make_cmd = ['make', '-j%d' % thread_count]
    install_cmd = ['make', 'install']
    setup_py_cmd = ['python', 'setup.py', '--prefix=%s/python/' % dst_dir]

    if os.path.exists(os.path.join(src_dir, 'setup.py')):
        utils.run(setup_py_cmd, src_dir)
    else:
        if not os.path.exists(os.path.join(src_dir, 'configure')):
            if os.path.exists(os.path.join(src_dir, 'autogen.sh')):
                utils.run(autogen_cmd, src_dir)
            else:
                raise RuntimeError('Nothing found to do in %s' % src_dir)

        ## FIXME: This pulseaudio thing should be a cli argument
        if src_dir.endswith('/efl'):
            utils.run(conf_cmd + ['--disable-pulseaudio'], src_dir)
        else:
            utils.run(conf_cmd, src_dir)

        utils.run(make_cmd, src_dir)
        utils.run(install_cmd, src_dir)

def main(args):
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

    ## FIXME: This and all deps must be declared somewhere
    # Hit the git
    efl = args['--efl']
    python_efl = args['--python-efl']
    econnman = args['--econnman']

    if not python_efl and econnman:
        python_efl = True

    if not efl and python_efl:
        efl = True

    git_packages = {
        'econnman': econnman,
        'python-efl': python_efl,
        'efl': efl,
    }

    package_dict = get_package_dict(mirror)

    download_packages(src_dir, mirror, package_dict)

    if any(git_packages.values()):
        download_git(src_dir, git_packages, package_dict)

    build_packages(package_dict, src_dir, instpath, thread_count=thread_count)

    print
    print 'DONE!'

    print
    print '(Remember to chown root and chmod u+s,a+x the freqset executable)'

# EOF

