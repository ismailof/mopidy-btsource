from __future__ import unicode_literals

from mopidy import models

URI_BT_ROOT = 'bt:root'
URI_BT_SCAN = 'bt:scan'
URI_BT_DEVICE = 'bt:dev'
URI_BT_SONG = 'bt:stream'

def translate_track_data (bt_track_data, uri=URI_BT_SONG):                                

    if bt_track_data:
        name = u''
        artists = None
        album = None
        length = 0
        genre = u''
        
        if 'Title' in bt_track_data:
            name = unicode(bt_track_data["Title"])
        if 'Artist' in bt_track_data:
            artists = [models.Artist(name=unicode(bt_track_data["Artist"]))]        
        if 'Album' in bt_track_data:
            album = models.Album(name=unicode(bt_track_data["Album"]))
        if 'Duration' in bt_track_data and bt_track_data["Duration"] != 0xFFFFFFFF:
            length = int(bt_track_data["Duration"])
        if 'Genre' in bt_track_data:
            genre = unicode(bt_track_data["Genre"])
                        
        return models.Track (uri=uri, name=name, artists=artists, album=album, length=length, genre=genre)    
    else:
        return {}
        
def format_track_data (track):  
    try:
        if track: 
            artist = ''
            title = ''
            for a in track.artists:        
                artist = a.name
                break
            title = track.name
            return '%s / %s' % (artist, title)
        else:
            return '<None>'
    except:
        return '<(Exception in format_track_data)>'
        
def format_play_time (msecs=0):
    try:
        if not msecs or msecs == 0xFFFFFFFF:
            strTime = '<n/a>'
        else:
            secs = msecs/1000
            strTime = '%dm%02ds' % (secs//60, secs%60)
        return strTime 
    except:
        return '<(Exception in format_play_time)>'
        