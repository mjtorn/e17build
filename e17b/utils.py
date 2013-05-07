# vim: encoding=utf-8

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

# EOF

