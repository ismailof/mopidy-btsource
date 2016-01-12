from __future__ import unicode_literals

import logging

from mopidy import backend
from mopidy import models
from mopidy.local import translator

from .helper import *
from .bt_player import BTPlayerController

HTTP_URI = '/btsource/'
ICON_BT = {'uri' : HTTP_URI + 'icon_bt_music.png',
         'width' : 150, 
         'height': 150}

logger = logging.getLogger(__name__)

class BTSourceLibWrapper(backend.LibraryProvider):
    """
    Entry in the library to manage Bluetooth Devices    
    It injects a simple uri "bt:something" so that the BTSource BackEnd is called
    TODO: Discovery Mode, Pairing and Trusting new devices
    """    
    root_directory = models.Ref.directory(uri=URI_BT_ROOT, name='BT Source')
    
    def __init__(self, backend):
        super(BTSourceLibWrapper, self).__init__(backend)        
        self.bt_player = BTPlayerController()                 
    
    def browse (self, uri):   
        logger.debug('Browse on %s', uri)
        
        result = []
        
        if uri == URI_BT_ROOT:
            #Root of the tree -> List of devices            
            #Discover directory
            result.append( models.Ref.directory(uri=URI_BT_SCAN, name='Scan for Devices') )            
            #TODO: Switch to discoverable mode (eas
            
            #Connected Device with Player ON 
            #TODO: List of discovered/known devices
            #TODO: URI includes device MAC or equivalent
            devName = self.bt_player.getDeviceName()    
            if devName:
                devUri = URI_BT_DEVICE
                result.append( models.Ref.playlist(uri=devUri, name=devName) )           
        elif uri == URI_BT_DEVICE:
            #Navigating the device. Show current Track
            current_track = translate_track_data(self.bt_player.get_current_track())
            result.append(models.Ref.track(uri=current_track.uri, name=current_track.name))
        elif uri == URI_BT_SCAN:
            #Add calls to start bluetooth scanning
            self.bt_player.scanDevices()
        
        return result
            
    def get_images(self, uris):          
        #Search for images on mopidy motor
        result = super(BTSourceLibWrapper, self).get_images(uris)
        #Add bluetooth image to BT devices
        for uri in uris:
            if uri in [URI_BT_DEVICE, URI_BT_SCAN] or not result[uri]:
                result[uri] = [models.Image(**ICON_BT)]                           
                    
        return result        
                        
    def lookup(self, uri):                  
        tracks = []
        if uri == URI_BT_SCAN:
            tracks.append(models.Track(uri=uri, name='Scan for Devices'))
        elif uri == URI_BT_SONG:                
            bt_current_track = self.bt_player.get_current_track()
            if bt_current_track:
                tracks.append(translate_track_data(bt_current_track, uri))
        
        logger.debug('Lookup on %s -> %s', uri, tracks)
        return tracks
    


    
    