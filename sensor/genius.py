
import asyncio
import logging

from homeassistant.const import (TEMP_CELSIUS)
from homeassistant.helpers.entity import Entity

_LOGGER = logging.getLogger(__name__)
GENIUS_LINK = 'genius_link'
DEPENDENCIES = ['genius']


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the Demo climate devices."""
    genius_utility = hass.data[GENIUS_LINK]
    await genius_utility.getjson('/zones')

    # Get sensors
    for sensor in genius_utility.getSensorList():
        async_add_entities([GeniusSensor(genius_utility, sensor)])

    # Get TRVs
    for trv in genius_utility.getTRVList():
        async_add_entities([GeniusTRV(genius_utility, trv)])


class GeniusSensor(Entity):
    """Representation of a Sensor."""

    def __init__(self, genius_utility, device):
        """Initialize the sensor."""
        GeniusSensor._genius_utility = genius_utility
        self._name = device['name']
        self._device_id = device['iID']
        self._device_addr = device['addr']
        self._battery = device['Battery']
        self._temperature = device['TEMPERATURE']
        self._luminance = device['LUMINANCE']
        self._motion = device['Motion']

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name + ":" + self._device_addr

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._temperature

    @property
    def unit_of_measurement(self):
        return TEMP_CELSIUS

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return {
            'Battery': self._battery,
            'Luminance': self._luminance,
            'Motion': self._motion
        }

    async def async_update(self):
        """Get the latest data."""
        device = GeniusSensor._genius_utility.getDevice(
            self._device_id, self._device_addr)
        data = GeniusSensor._genius_utility.getSensor(device)
        self._battery = data['Battery']
        self._temperature = data['TEMPERATURE']
        self._luminance = data['LUMINANCE']
        self._motion = data['Motion']


class GeniusTRV(Entity):
    """Representation of a Sensor."""

    def __init__(self, genius_utility, device):
        """Initialize the sensor."""
        GeniusSensor._genius_utility = genius_utility
        self._name = device['name']
        self._device_id = device['iID']
        self._device_addr = device['addr']
        self._battery = device['Battery']
        self._temperature = device['TEMPERATURE']

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name + ":" + self._device_addr

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._temperature

    @property
    def unit_of_measurement(self):
        return TEMP_CELSIUS

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return {
            'Battery': self._battery
        }

    async def async_update(self):
        """Get the latest data."""
        device = GeniusSensor._genius_utility.getDevice(
            self._device_id, self._device_addr)
        data = GeniusSensor._genius_utility.getTRV(device)
        self._battery = data['Battery']
        self._temperature = data['TEMPERATURE']
