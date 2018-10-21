"""
Genius hub platform that offers reading temperature and valve settings.

"""

import asyncio
import logging
import voluptuous as vol

from homeassistant.components.climate import (
    ClimateDevice, STATE_ECO, STATE_HEAT, STATE_MANUAL, STATE_OFF, STATE_ON, SUPPORT_TARGET_TEMPERATURE, SUPPORT_OPERATION_MODE, SUPPORT_ON_OFF)


from homeassistant.const import TEMP_CELSIUS, ATTR_TEMPERATURE

_LOGGER = logging.getLogger(__name__)
GENIUS_LINK = 'genius_link'

SUPPORT_FLAGS = SUPPORT_TARGET_TEMPERATURE | SUPPORT_OPERATION_MODE | SUPPORT_ON_OFF
# OPERATION_LIST = [STATE_HEAT, STATE_ECO, STATE_MANUAL, STATE_OFF, STATE_ON]
OPERATION_LIST = ['idle', 'cool', 'heat']
# OPERATION_LIST = ["AUTO", "COOL", "ECO", "HEAT", "OFF"]


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the Demo climate devices."""
    genius_utility = hass.data[GENIUS_LINK]
    await genius_utility.getjson('/zones')

    # Get the zones with a temperature
    climate_list = filter(
        lambda item: item['iType'] == 3, genius_utility.getAllZones())

    for zone in climate_list:
        climate_id, name, current_temperature, set_temperature, mode = genius_utility.GET_CLIMATE(
            zone)

        async_add_entities([GeniusClimate(genius_utility, name, climate_id, mode,
                                          set_temperature, current_temperature)])


class GeniusClimate(ClimateDevice):
    """Representation of a demo climate device."""

    def __init__(self, genius_utility, name, device_id, mode, target_temperature, current_temperature):
        """Initialize the climate device."""
        GeniusClimate._genius_utility = genius_utility
        self._name = name.strip()
        self._support_flags = SUPPORT_FLAGS
        self._target_temperature = target_temperature
        self._unit_of_measurement = TEMP_CELSIUS
        self._current_temperature = current_temperature
        self._device_id = device_id
        self._mode = mode

        if self._mode == "off":
            self._on = False
        else:
            self._on = True

        self._operation_list = OPERATION_LIST
        # ["off", "timer","footprint", "away", "boost", "early"]

    @property
    def supported_features(self):
        """Return the list of supported features."""
        return self._support_flags

    @property
    def name(self):
        """Return the name of the climate device."""
        return self._name

    @property
    def temperature_unit(self):
        """Return the unit of measurement."""
        return self._unit_of_measurement

    @property
    def current_temperature(self):
        """Return the current temperature."""
        return self._current_temperature

    @property
    def target_temperature(self):
        """Return the temperature we try to reach."""
        return self._target_temperature

    @property
    def current_operation(self):
        """Return the current operation mode."""
        """ Map between HA and Genius Hub """
        # ["off", "timer","footprint", "away", "override", "early"]
        # OPERATION_LIST = [STATE_HEAT, STATE_ECO, STATE_MANUAL, STATE_OFF, STATE_ON]
        # "AUTO", "COOL", "ECO", "HEAT", and "OFF"
        # OPERATION_LIST =[ 'idle', 'cool', 'heat']

        if self._mode == "off":
            self._on = False
            return "idle"

        if self._mode == "footprint":
            self._on = True
            return "cool"

        if self._mode == "away":
            self._on = False
            return "idle"

        if self._mode == "override":
            self._on = True
            return "heat"

        self._on = True
        return "heat"

    @property
    def operation_list(self):
        """Return the list of available operation modes."""
        return OPERATION_LIST

    async def async_set_operation_mode(self, operation_mode):
        """Set new target temperature."""
        _LOGGER.info("GeniusClimate set operation mode called!")
        if operation_mode == "idle":
            self._mode = "off"
        # elif operation_mode == "heat":
        #    self._mode = "override"
        elif operation_mode == "heat":
            self._mode = "footprint"
        elif operation_mode == "cool":
            self._mode = "off"
        # elif operation_mode == "heat":
        #    self._mode = "on"

        await GeniusClimate._genius_utility.putjson(self._device_id, '/mode', self._mode)

    @property
    def is_on(self):
        """Return true if the device is on."""
        return self._on

    async def async_set_temperature(self, **kwargs):
        """Set new target temperatures."""
        _LOGGER.info("GeniusClimate set temperature called!")
        if kwargs.get(ATTR_TEMPERATURE) is not None:
            self._target_temperature = kwargs.get(ATTR_TEMPERATURE)
            await GeniusClimate._genius_utility.putjson(self._device_id, {'iBoostTimeRemaining': 900, 'fBoostSP': self._target_temperature})

    async def async_update(self):
        """Get the latest data."""
        _LOGGER.info("GeniusClimate update called!")
        zone = GeniusClimate._genius_utility.getZone(self._device_id)
        if zone:
            dummy, dummy, self._current_temperature, self._set_temperature, self._mode = GeniusClimate._genius_utility.GET_CLIMATE(
                zone)
            if self._mode == "off":
                self._on = False
            else:
                self._on = True

    async def async_turn_on(self, **kwargs):
        """Turn on."""
        _LOGGER.info("GeniusClimate turn on called!")
        await GeniusClimate._genius_utility.putjson(self._device_id, {"fBoostSP": 1, "iBoostTimeRemaining": 900, "iMode": 16})

    async def async_turn_off(self, **kwargs):
        """Turn off."""
        _LOGGER.info("GeniusClimate turn off called!")
        await GeniusClimate._genius_utility.putjson(self._device_id, {"iMode": 1})
