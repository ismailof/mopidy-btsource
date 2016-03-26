from __future__ import unicode_literals

import logging
import os

from mopidy import config, ext

from .frontend import BTSourceFrontend
from .backend import BTSourceBackend

__version__ = '0.4.1'

logger = logging.getLogger(__name__)


class Extension(ext.Extension):

    dist_name = 'Mopidy-BTSource'
    ext_name = 'btsource'
    version = __version__

    def get_default_config(self):
        conf_file = os.path.join(os.path.dirname(__file__), 'ext.conf')
        return config.read(conf_file)

    def setup(self, registry):
        registry.add('frontend', BTSourceFrontend)
        registry.add('backend', BTSourceBackend)

        registry.add('http:static', {
            'name': self.ext_name,
            'path': os.path.join(os.path.dirname(__file__), 'public'),
        })
