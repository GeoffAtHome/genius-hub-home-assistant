"""
Genius hub platform that offers reading of current sensors.

In the future this may be extended to change the sensors.

"""

import socket
import voluptuous as vol

from homeassistant.components.climate import (
    ClimateDevice, SUPPORT_TARGET_TEMPERATURE, SUPPORT_OPERATION_MODE, SUPPORT_ON_OFF, PLATFORM_SCHEMA)
from homeassistant.const import TEMP_CELSIUS, ATTR_TEMPERATURE, CONF_HOST, CONF_API_KEY
import homeassistant.helpers.config_validation as cv

import json
import requests


SUPPORT_FLAGS = SUPPORT_TARGET_TEMPERATURE | SUPPORT_OPERATION_MODE | SUPPORT_ON_OFF

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST): cv.string,
    vol.Required(CONF_API_KEY): cv.string,
})

HG_URL = "https://my.geniushub.co.uk/v1"


def getjson(host, api_key, identifier):
    """ gets the json from the supplied zone identifier """
    url = host + identifier
    try:
        headers = {'Authorization': 'Bearer ' + api_key}
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return json.loads(response.text)

    except Exception as ex:
        print("Failed requests in getjsonfromhttp")
        print(ex)
        return None


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the Demo climate devices."""
    host = config.get(CONF_HOST)
    api_key = config.get(CONF_API_KEY)

    zone_list = getjson(HG_URL, api_key, '/zones')

    for zone in zone_list:
        if 'temperature' in zone:
            current_temperature = zone['temperature']
            target_temperature = zone['setpoint']
            name = zone['name']
            id = zone['id']
            mode = zone['mode']

            add_devices([GeniusDevice(name, id, mode,
                                      target_temperature, current_temperature)])


class GeniusDevice(ClimateDevice):
    """Representation of a demo climate device."""

    def __init__(self, name, device_id, mode, target_temperature, current_temperature):
        """Initialize the climate device."""
        self._name = name
        self._support_flags = SUPPORT_FLAGS
        self._target_temperature = target_temperature
        self._unit_of_measurement = TEMP_CELSIUS
        self._current_temperature = current_temperature
        self._device_id = device_id
        self._current_operation = mode

        if self._current_operation == "off":
            self._on = False
        else:
            self._on = True

        self._operation_list = ["off", "timer",
                                "footprint", "away", "boost", "early"]

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
        """Return current operation ie. heat, cool, idle."""
        return self._current_operation

    @property
    def operation_list(self):
        """Return the list of available operation modes."""
        return self._operation_list

    @property
    def is_on(self):
        """Return true if the device is on."""
        return self._on

    def set_temperature(self, **kwargs):
        """Set new target temperatures."""
        if kwargs.get(ATTR_TEMPERATURE) is not None:
            self._target_temperature = kwargs.get(ATTR_TEMPERATURE)
        self.schedule_update_ha_state()

    def set_operation_mode(self, operation_mode):
        """Set new target temperature."""
        self._current_operation = operation_mode
        self.schedule_update_ha_state()

    def update(self):
        """Get the latest date."""
        ''' self._current_temperature, self._target_temperature, mode = self._genius_utility.GET_TEMPERATURE(
            self._key)
        self._current_operation = self._genius_utility.GET_MODE(mode) '''
        self.schedule_update_ha_state()

    def turn_on(self):
        """Turn on."""
        self._on = True
        self.schedule_update_ha_state()

    def turn_off(self):
        """Turn off."""
        self._on = False
        self.schedule_update_ha_state()
