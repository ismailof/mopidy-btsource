from __future__ import unicode_literals

import logging

from mopidy import backend
from mopidy import models

from .helper import *
from .bt_player import BTPlayerController, BTPlayerUri

logger = logging.getLogger(__name__)

class BTSourcePlaybackProvider(backend.PlaybackProvider):
   
    def __init__(self, audio, backend):
        super(BTSourcePlaybackProvider, self).__init__(audio, backend)
       
        self.bt_player = BTPlayerController()

    #Orders to BT-Player       
    
    def play(self):        
        self.bt_player.play()
        return True    
    
    def resume(self):
        self.bt_player.play()
        return True
    
    def pause(self):
        self.bt_player.pause()
        return True
        
    def stop(self):
        self.bt_player.stop()
        return True

    def get_time_position(self):                 
        return self.bt_player.get_time_position()            
        
    def seek(self, position):
        return False           
               
    def translate_uri(self, uri):
        if uri != BTPlayerUri.BT_SONG:
            return None
        else:
            return 'appsrc://' + uri
    
    def prepare_change(self):
        return True
    
    def change_track(self, track):
        return track is not None