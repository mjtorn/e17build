# vim: fileencoding=utf-8

from .base import EnlightenmentBuilder

BUILD_ORDER = (
    # libs
    'rel/libs/efl', 'rel/libs/evas_generic_loaders', 'rel/libs/emotion_generic_players', 'rel/libs/elementary',
    ## Maybe later
    # 'rel/libs/webkit-efl',
    # apps
    'rel/apps/enlightenment', 'rel/apps/econnman', 'rel/apps/enventor', 'rel/apps/terminology',
    'rel/apps/epour', 'rel/apps/rage',
    # bindings
    'rel/bindings/python',
)

class E19Builder(EnlightenmentBuilder):
    """Build e19
    """

    version = '0.19'

    def __init__(self, args, build_order=BUILD_ORDER):
        """Set kwargs from this file
        """

        self.args = args
        self.build_order = args['PACKAGE'] or BUILD_ORDER

# EOF

