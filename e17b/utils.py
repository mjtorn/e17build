# vim: encoding=utf-8

def is_interesting(link):
    """Look at link and see if we want take note of it
    """

    return '.tar' in link.attrib['href'] and link.attrib['href'].endswith('bz2')

def pkg_name_sort(link1, link2):
    """Sort links by package name
    """

    url1 = link1.attr('href')
    url2 = link2.attr('href')

    pkg_name1 = url1.split('-', 1)[0]
    pkg_name2 = url2.split('-', 1)[0]

    return cmp(pkg_name1, pkg_name2)

# EOF

