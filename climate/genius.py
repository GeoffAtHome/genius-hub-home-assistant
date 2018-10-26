"""
Genius hub platform that offers reading temperature and valve settings.

"""

import asyncio
import logging
import voluptuous as vol

from homeassistant.components.climate import (
    ClimateDevice, STATE_ECO, STATE_HEAT, STATE_AUTO, STATE_IDLE, STATE_OFF, STATE_ON, SUPPORT_TARGET_TEMPERATURE, SUPPORT_OPERATION_MODE, SUPPORT_ON_OFF, SUPPORT_AWAY_MODE)


from homeassistant.const import TEMP_CELSIUS, ATTR_TEMPERATURE

_LOGGER = logging.getLogger(__name__)
GENIUS_LINK = 'genius_link'

SUPPORT_FLAGS = SUPPORT_TARGET_TEMPERATURE | SUPPORT_OPERATION_MODE | SUPPORT_ON_OFF | SUPPORT_AWAY_MODE
# Genius supports the operation modes: Off, Override, Footprint and Timer
# To work with Alexa these MUST BE
#
#   climate.STATE_HEAT: 'HEAT',
#   climate.STATE_COOL: 'COOL',
#   climate.STATE_AUTO: 'AUTO',
#   climate.STATE_ECO: 'ECO',
#   climate.STATE_IDLE: 'OFF',
#   climate.STATE_FAN_ONLY: 'OFF',
#   climate.STATE_DRY: 'OFF',

# These needed to be mapped into HA modes:
# Off       => OFF      => STATE_IDLE   # Mode_Off: 1,
# Override  => HEAT     => STATE_HEAT # Mode_Boost: 16,
# Footprint => ECO      => STATE_ECO    # Mode_Footprint: 4,
# Timer     => AUTO     => STATE_AUTO   # Mode_Timer: 2,
# Away                      # Mode_Away: 8,
#
OPERATION_LIST = [STATE_IDLE, STATE_HEAT, STATE_ECO, STATE_AUTO]


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the Demo climate devices."""
    genius_utility = hass.data[GENIUS_LINK]
    await genius_utility.getjson('/zones')

    # Get the zones with a temperature
    climate_list = genius_utility.getClimateList()

    for zone in climate_list:
        climate_id, name, current_temperature, set_temperature, mode, is_active = genius_utility.GET_CLIMATE(
            zone)

        async_add_entities([GeniusClimate(genius_utility, name, climate_id, mode,
                                          set_temperature, current_temperature, is_active)])


class GeniusClimate(ClimateDevice):
    """Representation of a demo climate device."""

    def __init__(self, genius_utility, name, device_id, mode, target_temperature, current_temperature, is_active):
        """Initialize the climate device."""
        GeniusClimate._genius_utility = genius_utility
        self._name = name.strip()
        self._support_flags = SUPPORT_FLAGS
        self._target_temperature = target_temperature
        self._unit_of_measurement = TEMP_CELSIUS
        self._current_temperature = current_temperature
        self._device_id = device_id
        self._mode = mode
        self._is_active = is_active
        self._operation_list = OPERATION_LIST

    @property
    def state(self):
        """Return the current state."""
        if self._is_active:
            return STATE_ON

        return STATE_OFF

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
        # These needed to be mapped into HA modes:
        # Off       => OFF      => STATE_IDLE   # Mode_Off: 1,
        # Override  => HEAT     => STATE_HEAT # Mode_Boost: 16,
        # Footprint => ECO      => STATE_ECO    # Mode_Footprint: 4,
        # Timer     => AUTO     => STATE_AUTO   # Mode_Timer: 2,
        # Away                      # Mode_Away: 8,
        #
        # OPERATION_LIST = [STATE_IDLE, STATE_HEAT, STATE_ECO, STATE_AUTO]
        if self._mode == "override":
            return STATE_HEAT
        if self._mode == "footprint":
            return STATE_ECO
        if self._mode == "timer":
            return STATE_AUTO

        return STATE_IDLE

    @property
    def min_temp(self):
        return 4.0

    @property
    def max_temp(self):
        return 28.0

    @property
    def operation_list(self):
        """Return the list of available operation modes."""
        return OPERATION_LIST

    @property
    def is_on(self):
        """Return true if the device is on."""
        if self._mode == "off":
            return False

        return True

    @property
    def is_away_mode_on(self):
        """Return true if away mode is on."""
        if self._mode == "away":
            return True

        return False

    async def async_set_operation_mode(self, operation_mode):
        """Set new target temperature."""
        _LOGGER.info("GeniusClimate set operation mode called!")
        _LOGGER.info(operation_mode)
        # These needed to be mapped into HA modes:
        # Off       => OFF      => STATE_IDLE   # Mode_Off: 1,
        # Override  => HEAT     => STATE_HEAT # Mode_Boost: 16,
        # Footprint => ECO      => STATE_ECO    # Mode_Footprint: 4,
        # Timer     => AUTO     => STATE_AUTO   # Mode_Timer: 2,
        # Away                      # Mode_Away: 8,
        #
        # OPERATION_LIST = [STATE_IDLE, STATE_HEAT, STATE_ECO, STATE_AUTO]
        data = {}
        if operation_mode == STATE_IDLE:
            self._mode = "off"
            data = {'iMode': 1}
        elif operation_mode == STATE_HEAT:
            self._mode = "override"
            data = {'iBoostTimeRemaining': 3600, 'iMode': 16,
                    'fBoostSP': self._target_temperature}
        elif operation_mode == STATE_ECO:
            self._mode = "footprint"
            data = {'iMode': 4}
        elif operation_mode == STATE_AUTO:
            self._mode = "timer"
            data = {'iMode': 2}
        else:
            _LOGGER.info("Unknown mode")
            return

        await GeniusClimate._genius_utility.putjson(self._device_id, data)

    async def async_set_temperature(self, **kwargs):
        """Set new target temperatures."""
        _LOGGER.info("GeniusClimate set temperature called!")
        if kwargs.get(ATTR_TEMPERATURE) is not None:
            self._target_temperature = kwargs.get(ATTR_TEMPERATURE)
            self._mode = "override"
            await GeniusClimate._genius_utility.putjson(self._device_id, {'iBoostTimeRemaining': 3600, 'fBoostSP': self._target_temperature, 'iMode': 16})

    async def async_update(self):
        """Get the latest data."""
        _LOGGER.info("GeniusClimate update called!")
        zone = GeniusClimate._genius_utility.getZone(self._device_id)
        if zone:
            dummy, dummy, self._current_temperature, self._set_temperature, self._mode, self._is_active = GeniusClimate._genius_utility.GET_CLIMATE(
                zone)
            _LOGGER.info(self._current_temperature,
                         self._set_temperature, self._mode, self._is_active)

    async def async_turn_on(self, **kwargs):
        """Turn on."""
        _LOGGER.info("GeniusClimate turn on called!")
        self._mode = "timer"
        await GeniusClimate._genius_utility.putjson(self._device_id, {"iMode": 2})

    async def async_turn_off(self, **kwargs):
        """Turn off."""
        _LOGGER.info("GeniusClimate turn off called!")
        self._mode = "off"
        await GeniusClimate._genius_utility.putjson(self._device_id, {"iMode": 1})
