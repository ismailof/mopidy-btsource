
from __future__ import unicode_literals

import dbus
import dbus.service
import dbus.mainloop.glib
import logging

from gi.repository import GObject


class BTPlayerUri(object):
    BT_ROOT = 'bt:root'
    BT_SCAN = 'bt:scan'
    BT_DEVICE = 'bt:dev'
    BT_SONG = 'bt:stream'


SERVICE_NAME = "org.bluez"
AGENT_IFACE = SERVICE_NAME + '.Agent1'
ADAPTER_IFACE = SERVICE_NAME + ".Adapter1"
DEVICE_IFACE = SERVICE_NAME + ".Device1"
CONTROL_IFACE = SERVICE_NAME + '.MediaControl1'
PLAYER_IFACE = SERVICE_NAME + '.MediaPlayer1'
TRANSPORT_IFACE = SERVICE_NAME + '.MediaTransport1'

logger = logging.getLogger(__name__)


class BTPlayerController(object):

    _instance = None

    bus = None
    mainloop = None
    adapter = None
    device = None
    deviceAlias = None
    player = None
    connected = False
    status = None
    position = None
    callback_fcns = {}
    track = []

    def __new__(self, *args, **kwargs):
        '''Make BTPlayerController a singleton so it can be called from the different submodules.
           Otherwise, several instances are run, and every dbus signal produces twice the events
           DISCLAIMER: I couldn't find a better way.
        '''
        if not self._instance:
            self._instance = super(BTPlayerController, self).__new__(self, *args, **kwargs)
        return self._instance

    def __init__(self):
        """Specify a signal handler, and find any connected media players"""
        if not self.bus:
            GObject.threads_init()
            dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

            self.bus = dbus.SystemBus()

            self.bus.add_signal_receiver(
                self.playerHandler,
                bus_name="org.bluez",
                dbus_interface="org.freedesktop.DBus.Properties",
                signal_name="PropertiesChanged",
                path_keyword="path")

            self.findAdapter()
            self.findPlayer()

    def start(self):
        """Start the BluePlayer by running the gobject Mainloop()"""
        self.mainloop = GObject.MainLoop()
        self.mainloop.run()

    def end(self):
        """Stop the gobject Mainloop()"""
        if(self.mainloop):
            self.mainloop.quit()

    def findPlayer(self):
        """Find any current media players and associated device"""
        manager = dbus.Interface(self.bus.get_object("org.bluez", "/"),
                                 "org.freedesktop.DBus.ObjectManager")
        objects = manager.GetManagedObjects()

        player_path = None
        for path, interfaces in objects.iteritems():
            if PLAYER_IFACE in interfaces:
                player_path = path
                break

        if player_path:
            self.connected = True
            self.getPlayer(player_path)
            player_properties = self.player.GetAll(PLAYER_IFACE,
                                                   dbus_interface="org.freedesktop.DBus.Properties")
            if "Track" in player_properties:
                self.track = player_properties["Track"]
                self._trigger_event('Track_Change', self.track)
            if "Position" in player_properties:
                self.position = int(player_properties["Position"])
                self._trigger_event('Position_Change', self.position)
            if "Status" in player_properties:
                self.status = str(player_properties["Status"])
                self._trigger_event('Status_Change', self.status)

            logger.info('Connected to bluetooth source %s', self.deviceAlias)
        else:
            logger.info('No bluetooth sources connected')

    def findAdapter(self):
        """Find any current media players and associated device"""
        manager = dbus.Interface(self.bus.get_object("org.bluez", "/"),
                                 "org.freedesktop.DBus.ObjectManager")
        objects = manager.GetManagedObjects()

        # adapter_path = manager.DefaultAdapter()
        for path, interfaces in objects.iteritems():
            if ADAPTER_IFACE in interfaces:
                adapter_path = path
                break

        if adapter_path:
            self.adapter = self.bus.get_object("org.bluez", adapter_path)
            adapter_properties = self.adapter.GetAll(ADAPTER_IFACE,
                                                     dbus_interface="org.freedesktop.DBus.Properties")
            logger.info("Found bluetooth adapter %s (%s)",
                        adapter_properties["Name"],
                        adapter_properties["Address"])

            # logger.info (adapter_properties)
        else:
            logger.info("No bluetooth adapters found")

    def scanDevices(self):
        # self.adapter.StartDiscovering(interface=ADAPTER_IFACE)
        self.adapter.Set(ADAPTER_IFACE,
                         'Discoverable',
                         True,
                         dbus_interface="org.freedesktop.DBus.Properties")
        pass

    def getPlayer(self, path):
        """Get a media player from a dbus path, and the associated device"""
        self.player = self.bus.get_object("org.bluez", path)
        device_path = self.player.Get(PLAYER_IFACE, "Device",
                                      dbus_interface="org.freedesktop.DBus.Properties")
        self.getDevice(device_path)

    def getDevice(self, path):
        """Get a device from a dbus path"""
        self.device = self.bus.get_object("org.bluez", path)
        self.deviceAlias = self.device.Get(DEVICE_IFACE, "Alias",
                                           dbus_interface="org.freedesktop.DBus.Properties")

    def playerHandler(self, interface, changed, invalidated, path):
        """Handle relevant property change signals"""
        iface = interface
        logger.debug("Interface: <{}> changed: {}".format(iface, changed))

        if iface == DEVICE_IFACE:
            # TODO: Avoid repetition
            if "Connected" in changed:
                if not changed["Connected"]:
                    self.connected = False
                    self.player = None
                    self._trigger_event('Connection_Change', self.connected)
        elif iface == CONTROL_IFACE:
            if "Connected" in changed:
                if changed["Connected"]:
                    self.findPlayer()
                    self._trigger_event('Connection_Change', self.connected)
        elif iface == PLAYER_IFACE:
            if "Track" in changed:
                self.track = changed["Track"]
                self._trigger_event('Track_Change', self.track)
            if "Position" in changed:
                self.position = int(changed["Position"])
                if self.position == 0xFFFFFFFF:
                    self.postion = None
                self._trigger_event('Position_Change', self.position)
            if "Status" in changed:
                self.status = str(changed["Status"])
                self._trigger_event('Status_Change', self.status)

    def next(self):
        logger.info('Sending Playback command to bluetooth player: NEXT')
        self.player.Next(dbus_interface=PLAYER_IFACE)

    def previous(self):
        logger.info('Sending Playback command to bluetooth player: PREVIOUS')
        self.player.Previous(dbus_interface=PLAYER_IFACE)

    def play(self):
        logger.debug('Sending Playback command to bluetooth player: PLAY')
        if self.status != 'playing':
            self.player.Play(dbus_interface=PLAYER_IFACE)

    def pause(self):
        logger.debug('Sending Playback command to bluetooth player: PAUSE')
        if self.status != 'paused':
            self.player.Pause(dbus_interface=PLAYER_IFACE)

    def stop(self):
        logger.debug('Sending Playback command to bluetooth player: STOP')
        if self.status != 'stopped':
            self.player.Stop(dbus_interface=PLAYER_IFACE)

    # FUNCIONES PROPIAS

    def get_device_name(self):
        if self.deviceAlias:
            return unicode(self.deviceAlias)
        else:
            return None

    def get_current_track(self):
        if self.player:
            bt_track = self.player.Get(PLAYER_IFACE, "Track",
                                       dbus_interface="org.freedesktop.DBus.Properties")
            if bt_track:
                self.track = bt_track
                return self.track
            else:
                return None
        else:
            return None

    def get_stream_title(self):
        # set of keywords used by common music players to indicate unknown artist
        # eg. ivoox player uses <unknown>
        unknown = {'<unknown>'}
        if self.player:
            bt_track = self.player.Get(PLAYER_IFACE, "Track",
                                       dbus_interface="org.freedesktop.DBus.Properties")
            if bt_track:
                track_name = bt_track.get('Title') \
                    if bt_track.get('Title') not in unknown else None
                track_artist = bt_track.get('Artist') \
                    if bt_track.get('Artist') not in unknown else None
                stream_title = ' - '.join([track_artist, track_name])
                return stream_title
            else:
                return None
        else:
            return None

    def get_player_state(self):
        if self.player:
            self.status = self.player.Get(PLAYER_IFACE, "Status",
                                          dbus_interface="org.freedesktop.DBus.Properties")
            return self.status
        else:
            return None

    def get_time_position(self):
        if self.player:
            position = self.player.Get(PLAYER_IFACE, "Position",
                                       dbus_interface="org.freedesktop.DBus.Properties")
            if position is not None and position != 0xFFFFFFFF:
                self.position = int(position)
            else:
                self.position = None
            return self.position
        else:
            return None

    def is_connected(self):
        return self.connected

    def register_event(self, event, callback):
        self.callback_fcns[event] = callback

    def _trigger_event(self, event, *args):
        if event in self.callback_fcns:
            callback = self.callback_fcns[event]
            logger.debug('Event %s triggered callback %s', event, callback.__name__)
            callback(*args)
        else:
            logger.debug('Event %s triggered with no callbacks associated', event)
