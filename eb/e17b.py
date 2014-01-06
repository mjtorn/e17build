# vim: encoding: utf-8

from .base import EnlightenmentBuilder

# These directories reflect the names of the packages
BUILD_ORDER = (
    # libs
    'rel/libs/efl', 'rel/libs/evas_generic_loaders', 'rel/libs/emotion_generic_players', 'rel/libs/elementary',
    'e_dbus',
    # apps
    'enlightenment', 'rel/apps/econnman', 'rel/apps/enventor', 'rel/apps/terminology',
    'etrophy', 'echievements', 'elemines',
    # bindings
    'rel/bindings/python',
)

class E17Builder(EnlightenmentBuilder):
    """Build e17
    """

    def __init__(self, args, build_order=BUILD_ORDER):
        """Set kwargs from this file
        """

        self.args = args
        self.build_order = BUILD_ORDER

# EOF

