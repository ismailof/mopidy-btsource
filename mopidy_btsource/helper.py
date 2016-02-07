from __future__ import unicode_literals
   
def format_track_data (track):  
    try:
        if track: 
            artists = ', '.join(track.artists)
            title = track.name
            return '%u - %u' % (artist, title)
        else:
            return '<Nothing playing>'
    except Exception as ex:
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
        