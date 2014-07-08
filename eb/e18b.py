# vim: encoding: utf-8

from .base import EnlightenmentBuilder

BUILD_ORDER = (
    # libs
    'rel/libs/efl', 'rel/libs/evas_generic_loaders', 'rel/libs/emotion_generic_players', 'rel/libs/elementary',
    'e_dbus',
    # apps
    'rel/apps/enlightenment', 'rel/apps/econnman', 'rel/apps/enventor', 'rel/apps/terminology',
    # 'etrophy', 'echievements', 'elemines',
    'etrophy', 'elemines',
    # bindings
    'rel/bindings/python',
)

class E18Builder(EnlightenmentBuilder):
    """Build e18
    """

    def __init__(self, args, build_order=BUILD_ORDER):
        """Set kwargs from this file
        """

        self.args = args
        self.build_order = args['PACKAGE'] or BUILD_ORDER

# EOF

