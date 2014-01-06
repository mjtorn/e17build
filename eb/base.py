# vim: encoding: utf-8

from . import utils

import os

class EnlightenmentBuilder(object):
    """Extend this class for different enlightenment versions
    """

    def __init__(self, args, build_order=None, skip_build=None):
        """Set some basic stuff into self before execution
        """

        raise NotImplementedError('Implement this in base class')

    def build_package(self, src_dir, dst_dir, thread_count=1, rebuild=False):
        """Build source into destination
        """

        ## XXX: The later additions mostly untested.
        aclocal_cmd = ['aclocal']
        autogen_cmd = ['./autogen.sh', '--prefix=%s' % dst_dir]
        conf_cmd = ['./configure', '--prefix=%s' % dst_dir]
        make_cmd = ['make', '-j%d' % thread_count]
        install_cmd = ['make', 'install']
        setup_py_cmd = ['python', 'setup.py', 'install', '--prefix=%s/python/' % dst_dir]

        if os.path.exists(os.path.join(src_dir, 'setup.py')):
            utils.run(setup_py_cmd, src_dir)
        else:
            if '/efl-' in src_dir:
                utils.run(aclocal_cmd, src_dir)

            if os.path.exists(os.path.join(src_dir, 'autogen.sh')):
                utils.run(autogen_cmd, src_dir)
            elif os.path.exists(os.path.join(src_dir, 'configure')):
                utils.run(conf_cmd, src_dir)
            else:
                raise RuntimeError('Nothing found to do in %s' % src_dir)

            utils.run(make_cmd, src_dir)
            utils.run(install_cmd, src_dir)

# EOF

