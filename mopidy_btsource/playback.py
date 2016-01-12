from __future__ import unicode_literals

import logging

from mopidy import backend
from mopidy import models

from .helper import *
from .bt_player import BTPlayerController

logger = logging.getLogger(__name__)

class BTSourcePlaybackProvider(backend.PlaybackProvider):
   
    def __init__(self, audio, backend):
        super(BTSourcePlaybackProvider, self).__init__(audio, backend)
       
        self.bt_player = BTPlayerController()
        self.audio = audio; 
        
        self.audio.prepare_change();
        self.audio.set_appsrc('none');   

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
    
    """ Override default playback functions to avoid operations on gstreamer """
    
    #INTERFAZ AUDIO    
    def emit_data(self, buffer_):
        return True
    
    def emit_end_of_stream(self):
        pass    
        
    def translate_uri(self, uri):
        if uri != URI_BT_SONG:
            return None
        else:
            return uri + ':appsrc//'
    
    def set_position(self, position):
        return False      

    def start_playback(self):
        #self.bt_player.play()
        return True

    def pause_playback(self):
        #self.bt_player.pause()
        return True

    def prepare_change(self):
        return True

    def stop_playback(self):
        self.bt_player.stop()
        return True

    def wait_for_state_change(self):
        pass

    def enable_sync_handler(self):
        pass

    def _set_state(self, state):
        return True

