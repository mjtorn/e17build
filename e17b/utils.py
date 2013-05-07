# vim: encoding=utf-8

def is_interesting(link):
    """Look at link and see if we want take note of it
    """

    return '.tar' in link.attrib['href']

# EOF

