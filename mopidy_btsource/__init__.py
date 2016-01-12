from __future__ import unicode_literals

import logging
import os

# TODO: Remove entirely if you don't register GStreamer elements below
import pygst
pygst.require('0.10')
import gst
import gobject

from mopidy import config, ext

from .frontend import BTSourceFrontend        
from .backend import BTSourceBackend            

__version__ = '0.2.5'

# TODO: If you need to log, use loggers named after the current Python module
logger = logging.getLogger(__name__)

class Extension(ext.Extension):

    dist_name = 'Mopidy-BTSource'
    ext_name = 'btsource'
    version = __version__    
    
    def get_default_config(self):
        conf_file = os.path.join(os.path.dirname(__file__), 'ext.conf')
        return config.read(conf_file)

    def get_config_schema(self):
        schema = super(Extension, self).get_config_schema()
        # TODO: Comment in and edit, or remove entirely
        #schema['username'] = config.String()
        #schema['password'] = config.Secret()
        return schema

    def setup(self, registry):           
        registry.add('frontend', BTSourceFrontend)
        registry.add('backend', BTSourceBackend)

        registry.add('http:static', {
            'name': self.ext_name,
            'path': os.path.join(os.path.dirname(__file__), 'public'),
        })     
    
