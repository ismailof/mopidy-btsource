from __future__ import unicode_literals

import logging

from mopidy import backend
from mopidy import models

from .bt_player import BTPlayerController, BTPlayerUri

HTTP_URI = '/btsource/'
ICON_BT = {'uri': HTTP_URI + 'icon_bt_music.png',
           'width': 150,
           'height': 150}

logger = logging.getLogger(__name__)


class BTSourceLibWrapper(backend.LibraryProvider):
    """
    Entry in the library to manage Bluetooth Devices
    TODO: Discovery Mode, Pairing and Trusting new devices
    """
    root_directory = models.Ref.directory(uri=BTPlayerUri.BT_ROOT,
                                          name='Bluetooth')

    def __init__(self, backend):
        super(BTSourceLibWrapper, self).__init__(backend)
        self.bt_player = BTPlayerController()

    def browse(self, uri):
        logger.debug('Browse on %s', uri)

        result = []

        if uri == BTPlayerUri.BT_ROOT:
            # Root of the tree -> List of devices
            # Discover directory
            result.append(models.Ref.directory(uri=BTPlayerUri.BT_SCAN,
                                               name='Scan for Devices'))
            # TODO: Switch to discoverable mode
            # Connected Device with Player ON
            # TODO: List of discovered/known devices
            # TODO: URI includes device MAC or equivalent (modalias?)
            if self.bt_player.is_connected():
                devName = self.bt_player.get_device_name()
                devUri = BTPlayerUri.BT_DEVICE
                result.append(models.Ref.track(uri=devUri, name=devName))
        elif uri == BTPlayerUri.BT_DEVICE:
            if self.bt_player.is_connected():
                # Navigating the device. Show current Track
                current_track = self.compose_bt_track(uri=BTPlayerUri.BT_SONG)
                result.append(models.Ref.track(uri=current_track.uri,
                                               name=current_track.name))
        elif uri == BTPlayerUri.BT_SCAN:
            # Add calls to start bluetooth scanning
            self.bt_player.scanDevices()
        return result

    def get_images(self, uris):
        if type(uris) in {str, unicode}:
            uris = [uris]
        # Add bluetooth image to BT URIs
        images = {}
        for uri in uris:
            if uri.startswith(BTPlayerUri.BT_SONG):
                images[uri] = [models.Image(**ICON_BT)]
            elif uri.startswith(BTPlayerUri.BT_DEVICE):
                # TODO: Different images per device type (phone, pc, etc)
                images[uri] = [models.Image(**ICON_BT)]
            elif uri == BTPlayerUri.BT_SCAN:
                images[uri] = [models.Image(**ICON_BT)]
            else:
                images[uri] = []
        return images

    def lookup(self, uris):
        # Make sure we have a list of uris
        if type(uris) in {str, unicode}:
            uris = [uris]
        logger.debug('Lookup on %r', uris)

        tracks = []
        for uri in uris:
            if uri.startswith(BTPlayerUri.BT_SONG):
                tracks.append(self.compose_bt_track(uri=BTPlayerUri.BT_SONG))
            elif uri.startswith(BTPlayerUri.BT_DEVICE):
                tracks.append(self.compose_bt_track(uri=BTPlayerUri.BT_SONG))
        return tracks

    def compose_bt_track(self, uri=BTPlayerUri.BT_SONG):
        # Old behaviour -> Use real track data on lookup
        # Since track data are immutable, it is hacky to change the data on track changes
        # New behaviour -> Use track structure with the device name and info
        if not self.bt_player.is_connected():
            return None
        dev_name = unicode(self.bt_player.get_device_name())
        bt_info = {'name': dev_name,
                   'artists': [models.Artist(name='Bluetooth Player')],
                   'album': models.Album(name=dev_name, uri=BTPlayerUri.BT_DEVICE),
                   'uri': uri}
        return models.Track(**bt_info)

    def translate_track_data(bt_track_data, uri):
        if bt_track_data:
            mp_track_data = {
                'uri': uri,
                'name': unicode(bt_track_data.get('Title', '')),
                'artists': [models.Artist(name=unicode(bt_track_data.get('Artist')))],
                'album': models.Album(name=unicode(bt_track_data.get('Album'))),
                'length': int(bt_track_data.get('Duration')) if bt_track_data.get('Duration') != 0xFFFFFFFF else None,
                'genre': unicode(bt_track_data.get('Genre'))}
            return models.Track(**mp_track_data)
        else:
            return {}
