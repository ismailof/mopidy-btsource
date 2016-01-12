from __future__ import unicode_literals

import logging
import pykka
from mopidy import core
from mopidy.core import CoreListener
from mopidy.core import PlaybackState

from .helper import *
from .bt_player import BTPlayerController

logger = logging.getLogger(__name__)

class BTSourceFrontend(pykka.ThreadingActor, CoreListener):

    def __init__(self, config, core):
        super(BTSourceFrontend, self).__init__()        
        self.core = core       
        
        self.bt_player = BTPlayerController()        
        #self.bt_player.register_callback('Connection_Change', self.bt_conn_changed)
        self.bt_player.register_callback('Status_Change', self.bt_state_changed)
        self.bt_player.register_callback('Track_Change', self.bt_track_changed)
        self.bt_player.register_callback('Position_Change', self.bt_position_changed)
        
        self.bt_track_selected = False;
        
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
        if self.bt_track_selected:
            if bt_state in translate_state:
                playback_state = translate_state[bt_state]
                logger.info ("BT Player state changed to '%s'", playback_state)
                self.core.playback.set_state(playback_state);
            else:
                logger.info ("BT Player state not recognized: '%s'", bt_state)
 
    def bt_track_changed (self, bt_track):         
        try:
            track = translate_track_data(bt_track)
            if track:            
                logger.info ('BT Track changed. Updating track info to %s', format_track_data(track))
                # UGLY HACK TO REFRESH SONG METADATA. Waiting for improved stream features on Mopidy
                # Erase all of the dummy bt songs and add new song to tracklist (pos 0)               
                tracks_removed = self.core.tracklist.remove(uri=[URI_BT_SONG]).get()         
                #logger.debug('Erased dummy BT songs: {}'.format(tracks_removed))
                #Add dummy song to tracklist if there was prevously one (at least)
                if tracks_removed:
                    self.core.tracklist.add(uri=URI_BT_SONG, at_position=0).get()                               
                # If BT Playing is selected play the song
                if self.bt_track_selected:
                    self.core.playback.play(tlid=0)    
                else:                
                    self.bt_player.stop()
        except Exception as ex:
            logger.info ('bt_source/frontend/bt_track_changed. Exception raised: {}', ex)
    
    def bt_position_changed (self, bt_position):       
        if self.bt_track_selected:
            if bt_position is not None:
                logger.info ('BT Position changed. Updating position to %s', format_play_time(bt_position))            
                self._update_core_position(bt_position)                        
            
     # Changes trigger by mopidy playback over CoreListener 
     # Mopidy -> BT Player                      

    def seeked(self, time_position): 
        #HACK to update clients: Currently BT Player is not seekable
        if self.bt_track_selected:
            if self.bt_player.is_connected():
                self._refresh_bt_position(time_position)      
        
    def track_playback_started(self, tl_track):
        if self.bt_player.is_connected():
            if self._check_bt_track():
                #To catch up the real playing position of the player  
                self.bt_track_selected = True
                self._refresh_bt_position()
            else:
                #Stop bluetooth source from playing audio
                self.bt_track_selected = False
                logger.info('Started playback of a non-BT Track. Stopping BT Player')
                self.bt_player.stop()                
    
    # Private helper functions            
    def _refresh_bt_position(self, core_position=None):        
        bt_position = self.bt_player.get_time_position()           
        if core_position is None:
            self._update_core_position(bt_position) 
        elif bt_position is not None:
            if abs(bt_position - core_position) > 1000:
                logger.debug ('Correcting mopidy core position %s to BT position: %s', format_play_time(core_position), format_play_time(bt_position) )                  
                self._update_core_position(bt_position) 
        
    #In case some day I find a better way than perform a seek() 
    #to inform mopidy core and the clients to update their position    
    def _update_core_position (self, position):
        self.core.playback.seek(position) 
            
    def _check_bt_track(self):
        #Use get_stream_title() when stream functionality is available?
        current_track = self.core.playback.get_current_track().get()
        if current_track:   
            return current_track.uri.startswith('bt:')
        else:
            return False                    