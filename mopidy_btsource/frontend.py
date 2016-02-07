from __future__ import unicode_literals

import logging
import time
import pykka
from mopidy import core
from mopidy.core import CoreListener
from mopidy.core import PlaybackState

from .helper import *
from .bt_player import BTPlayerController, BTPlayerUri

logger = logging.getLogger(__name__)

class BTSourceFrontend(pykka.ThreadingActor, CoreListener):

    def __init__(self, config, core):
        super(BTSourceFrontend, self).__init__()        
        self.core = core       
        
        self.bt_player = BTPlayerController()        
        #self.bt_player.register_event('Connection_Change', self.bt_conn_changed)
        self.bt_player.register_event('Status_Change', self.bt_state_changed)
        self.bt_player.register_event('Track_Change', self.bt_track_changed)
        self.bt_player.register_event('Position_Change', self.bt_position_changed)
        
        self._is_bt_selected = False;
        
    def on_start(self):
        pass
        
    def on_stop(self):
        pass
            

    ## Functions triggered by changes on bluetooth player
    ##    BT Player -> Mopidy     
 
    def bt_state_changed (self, bt_state):       
        translate_state = {'playing':PlaybackState.PLAYING,
                           'paused':PlaybackState.PAUSED,
                           'stopped':PlaybackState.STOPPED
                           }
        if self._is_bt_selected:
            if bt_state in translate_state:
                playback_state = translate_state[bt_state]
                logger.debug ("BT Player state changed to '%s'", playback_state)
                if self.core.playback.get_state().get() != playback_state:
                    self.core.playback.set_state(playback_state);
            else:
                logger.debug ("BT Player state not recognized: '%s'", bt_state)
 
    def bt_track_changed (self, bt_track):         
        try:            
            if self._is_bt_selected:
                if bt_track:                            
                    stream_title = self.bt_player.get_stream_title()
                    logger.debug ('BT Track changed. Updating stream title to %r', stream_title)
                    self._set_stream_title(stream_title)                    
                else:
                    self._set_stream_title(None)
            else:                
                #HACK: If bluetooth uri is not selected, stop source bluetooth to avoid simultaneous playing
                self.bt_player.stop()
                
        except Exception as ex:
            logger.info ('bt_source/frontend/bt_track_changed. Exception raised: %r', ex)
    
    def bt_position_changed (self, bt_position):       
        if self._is_bt_selected:
            if bt_position is not None:
                logger.debug ('BT Position changed. Updating position to %s', format_play_time(bt_position))            
                self._update_core_position(bt_position)                        
            
     # Changes trigger by mopidy playback over CoreListener 
     # Mopidy -> BT Player                      

    def seeked(self, time_position): 
        #HACK to update clients: Currently BT Player is not seekable
        if self.bt_player.is_connected():
            if self._is_bt_selected:            
                self._refresh_bt_position(time_position)      
  
    #def track_playback_resumed(self, tl_track):
        #if self.bt_player.is_connected():
            #if self._is_bt_track(tl_track):                
                #self.send ('stream_title_changed', title=self.bt_player.get_stream_title())
  
    def track_playback_started(self, tl_track):        
        if self.bt_player.is_connected():
            if self._is_bt_track(tl_track):          
                self._is_bt_selected = True                  
                self._set_stream_title(self.bt_player.get_stream_title())
                self._refresh_bt_position()
            else: 
                if self._is_bt_selected:
                    self._set_stream_title(None)
                    self._is_bt_selected = False
                #Stop bluetooth source from playing audio
                logger.debug('Started playback of a non-BT Track. Stopping BT Player')                
                self.bt_player.stop()                                                
    
    #Updates position to clients to the position resported by the player
    def _refresh_bt_position(self, core_position=None):        
        bt_position = self.bt_player.get_time_position()           
        if core_position is None:
            self._update_core_position(bt_position) 
        elif bt_position is not None:
            if abs(bt_position - core_position) > 1000:
                logger.debug ('Correcting mopidy core position %s to BT position: %s', format_play_time(core_position), format_play_time(bt_position) )                  
                self._update_core_position(bt_position) 
        
    #Corrects position in clients to the position resported by the player
    def _update_core_position (self, position):
        time.sleep (0.1)
        self.send('seeked', time_position=position)
        
    #Use get_stream_title() when stream functionality is available?        
    def _is_bt_track(self, tl_track):        
        return tl_track.track.uri.startswith('bt:') if tl_track else False     

    def _set_stream_title(self, title):  
        #It seems for now there is no method to update the value of stream_title in playback         
        self.core.playback._stream_title = title
        self.send ('stream_title_changed', title=title)        
        #At least notify the clients
        #