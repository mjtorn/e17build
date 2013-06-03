# vim: encoding=utf-8

from distutils import sysconfig

import os

import shutil

import subprocess

import tarfile

import urllib2

DOWNLOAD_RETRIES = 3
DOWNLOAD_TIMEOUT = 10

def is_interesting(link):
    """Look at link and see if we want take note of it
    """

    return '.tar' in link.attrib['href'] and link.attrib['href'].endswith('bz2')

def name_from_link(link):
    """Extract package name from link
    """

    url = link.attr('href')

    # FIXME: This is painful, but eg .rsplit('-', 1)[0] fails with 1.7.0-beta and
    # we need to support eg. python-emotion
    if 'python' in url:
        return '-'.join(url.split('-', 2)[:2])
    return url.split('-', 1)[0]

def pkg_name_sort(link1, link2):
    """Sort links by package name
    """

    pkg_name1 = name_from_link(link1)
    pkg_name2 = name_from_link(link2)

    return cmp(pkg_name1, pkg_name2)

def dep_order(pkgs, pkg1, pkg2):
    """Look for pkg1 and pkg2 in pkgs and make sure they're in that order
    """

    try:
        pkg1_idx = pkgs.index(pkg1)

        try:
            pkg2_idx = pkgs.index(pkg2)
        except ValueError:
            pkg2_idx = None
            print '%s not found' % pkg2
    except ValueError:
        pkg1_idx = None
        print '%s not found' % pkg1

    if pkg1_idx is not None and pkg2_idx is not None:
        if pkg1_idx > pkg2_idx:
            pkg1_ = pkgs.pop(pkg1_idx)
            pkgs.insert(pkg2_idx, pkg1_)

def download(url, dst_file):
    """Download url into local file
    """

    retries = DOWNLOAD_RETRIES

    while retries:
        retries -= 1

        try:
            url = urllib2.urlopen(url, timeout=DOWNLOAD_TIMEOUT)
            break
        except urllib2.HTTPError, e:
            print 'HTTPError %s' % e
        except urllib2.URLError, e:
            print 'URLError %s' % e

    with open(dst_file, 'wb') as dst:
        ## Y U NO TELL ABOUT EOF o,,
        # while True:
        #     for chunk in url.read(1024):
        #         # print 'Chunk: "%s"' % chunk
        #         dst.write(chunk)
        #         if chunk == '':
        #             url.close()
        #             break

        dst.write(url.read())
        url.close()

    dst.close()

def safe_tar_files(tar, verbose=False):
    """Although we trust e17 devs, be safe ;)
    """

    unsafe = (os.sep, '..',)

    for file_info in tar:
        for s in unsafe:
            if file_info.name.startswith(s):
                print 'Malicious file found! %s' % file_info.name
                raise IOError('Refusing %s' % file_info.name)

        if verbose:
            print '[%8d] %s' % (file_info.size, file_info.name)

        yield file_info

def verify_clean_build_dir(dst, tar):
    """Where does this tar extract? Remove old, if exists
    Returns the name of the dir
    """

    found_main_dir = None
    for file_info in tar:
        if file_info.type == tarfile.DIRTYPE:
            dir_name = file_info.name
            elems = os.path.split(dir_name)
            if len(elems) == 2 and elems[0] == '':
                if found_main_dir is not None:
                    raise NotImplementedError('Two dirs in %s' % tar.name)

                found_main_dir = dir_name

    if found_main_dir is None:
        raise ValueError('We need a directory to work with %s' % tar.name)

    dst_dir = os.path.join(dst, found_main_dir)
    remove_if_exists(dst_dir)

    return dst_dir

def remove_if_exists(dir_):
    """Does what it says it does
    """

    if os.path.exists(dir_):
        print 'Delete %s' % dir_
        shutil.rmtree(dir_)

def run(cmd, dir_):
    """Try running a command in a directory, raise exception on failure
    """

    print '[%s] %s' % (dir_, ' '.join(cmd))
    retval = subprocess.call(cmd, cwd=dir_)

    if retval != 0:
        raise RuntimeError('%s exited %d' % (' '.join(cmd), retval))

def setup_environment(dst_dir):
    """Sets the build environment. Based on easy_e17.sh
    """

    paths = (
        ('PATH', os.path.join(dst_dir, 'bin')),
        ('LD_LIBRARY_PATH', os.path.join(dst_dir, 'lib')),
        ('PKG_CONFIG_PATH', os.path.join(dst_dir, 'lib', 'pkgconfig')),
    )

    # This is mostly to work through my crap, but it doesn't kill anything
    for env_var, path in paths:
        env_val = os.environ.get(env_var, '')
        env_vals = env_val.split(':')
        env_vals = [val for val in env_vals if not 'e17' in val]
        env_vals.insert(0, path)

        os.environ[env_var] = ':'.join(env_vals)

    os.environ['PYTHONPATH'] = sysconfig.get_python_lib(prefix=dst_dir)
    os.environ['PYTHONINCLUDE'] = sysconfig.get_python_inc(prefix=dst_dir)

    # XXX: Not sure if there's a reason the arguments are in different orders
    # so I won't generalize these. Some copypasta might be good for you.
    aclocal_path = os.path.join(dst_dir, 'share', 'aclocal')
    aclocal_flags = os.environ.get('ACLOCAL_FLAGS', '')
    aclocal_flags = '-I %s %s' % (aclocal_path, aclocal_flags)
    os.environ['ACLOCAL_FLAGS'] = aclocal_flags.strip()

    cpp_path = os.path.join(dst_dir, 'include')
    cpp_flags = os.environ.get('CPPFLAGS', '')
    cpp_flags = '%s -I%s' % (cpp_flags, cpp_path)
    os.environ['CPPFLAGS'] = cpp_flags.strip()

    ld_path = os.path.join(dst_dir, 'lib')
    ld_flags = os.environ.get('LDFLAGS', '')
    ld_flags = '%s -L%s' % (ld_flags, ld_path)
    os.environ['LDFLAGS'] = ld_flags.strip()

def get_thread_count():
    """Get the thread count for make -j
    """

    f = open(os.path.join(os.path.sep, 'proc', 'cpuinfo'), 'rb')
    cpus = [l for l in f.readlines() if l.startswith('processor')]

    # And +1 for io sleeping
    return len(cpus) + 1

# EOF

