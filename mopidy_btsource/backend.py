from __future__ import unicode_literals

import pykka
import logging

from mopidy import backend

from .library   import BTSourceLibWrapper
from .playback  import BTSourcePlaybackProvider

logger = logging.getLogger(__name__)

class BTSourceBackend(
        pykka.ThreadingActor, backend.Backend):        

    def __init__(self, config, audio):
        super(BTSourceBackend, self).__init__()

        self.config = config

        self.library = BTSourceLibWrapper(backend=self)        
        self.playback = BTSourcePlaybackProvider(audio=audio, backend=self)
                
        self.uri_schemes = ['bt']   

        #To avoid GStreamer from transmitting anything
        audio.prepare_change();
        audio.set_appsrc('raw'); 

    def on_start(self):
        pass

    def on_stop(self):
        pass
       