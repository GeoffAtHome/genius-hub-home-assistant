"""
homeassistant.components.switch.genius
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Implements Genius switches.
"""

import logging
import asyncio
from homeassistant.components.switch import SwitchDevice

_LOGGER = logging.getLogger(__name__)
GENIUS_LINK = 'genius_link'


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """ Find and return Genius switches """
    switches = []
    genius_utility = hass.data[GENIUS_LINK]
    await genius_utility.getjson('/zones')

    # Get the zones that are switches
    switch_list = filter(
        lambda item: item['iType'] == 2, genius_utility.getAllZones())

    for zone in switch_list:
        switch_id, name, mode = genius_utility.GET_SWITCH(zone)
        switches.append(GeniusSwitch(genius_utility, switch_id, name, mode))

    async_add_entities(switches)


class GeniusSwitch(SwitchDevice):
    """ Provides a Genius switch. """

    def __init__(self, genius_utility, device_id, name, state):
        GeniusSwitch._genius_utility = genius_utility
        self._name = name.strip()
        self._device_id = device_id
        if state == 'off':
            self._state = False
        else:
            self._state = True

    @property
    def name(self):
        """ Returns the name of the Genius switch. """
        return self._name

    @property
    def is_on(self):
        """ True if Genius switch is on. """
        return self._state

    async def async_update(self):
        """Get the latest data."""
        zone = GeniusSwitch._genius_utility.getZone(self._device_id)
        if zone:
            mode = GeniusSwitch._genius_utility.GET_MODE(zone)
            if mode == 'off':
                self._state = False
            else:
                self._state = True

    async def async_turn_on(self, **kwargs):
        """ Turn the Genius switch on. """
        duration = 24 * 60 * 60 # 24 hours in seconds
        await GeniusSwitch._genius_utility.putjson(self._device_id, {"fBoostSP": 1, "iBoostTimeRemaining": duration, "iMode": 16})

    async def async_turn_off(self, **kwargs):
        """ Turn the Genius switch off. """
        await GeniusSwitch._genius_utility.putjson(self._device_id, {"iMode": 1})
