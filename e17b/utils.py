# vim: encoding=utf-8

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

# EOF

