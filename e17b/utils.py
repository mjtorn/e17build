# vim: encoding=utf-8

import os

import shutil

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

    return url.split('-', 1)[0]

def pkg_name_sort(link1, link2):
    """Sort links by package name
    """

    pkg_name1 = name_from_link(link1)
    pkg_name2 = name_from_link(link2)

    return cmp(pkg_name1, pkg_name2)

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
    if os.path.exists(dst_dir):
        print 'Delete old %s' % dst_dir
        shutil.rmtree(dst_dir)

    return dst_dir

def remove_if_exists(dir):
    """Does what it says it does
    """

    if os.path.exists(dir):
        print 'Delete %s' % dir
        shutil.rmtree(dir)

# EOF

