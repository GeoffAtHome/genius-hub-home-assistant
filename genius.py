
''' This module contains utility functions that are shared across other programs '''
import json
import requests
import time
import threading
import logging
import voluptuous as vol

from homeassistant.const import CONF_API_KEY
from homeassistant.helpers import config_validation as cv

_LOGGER = logging.getLogger(__name__)

GENIUS_LINK = 'genius_link'
DOMAIN = 'genius'

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_API_KEY): cv.string,
    })
}, extra=vol.ALLOW_EXTRA)


async def async_setup(hass, config):
    """Try to start embedded Lightwave broker."""
    _LOGGER.info("Genius broker started!")
    api_key = config[DOMAIN].get(CONF_API_KEY)
    _LOGGER.info("Genius broker api key: " + api_key)
    hass.data[GENIUS_LINK] = GeniusUtility(api_key)
    _LOGGER.info("Genius  broker complete!")
    return True


class GeniusUtility():
    HG_URL = "https://my.geniushub.co.uk/v1"
    UPDATE_INTERVAL = 15  # Interval between fetching new data from the Genius hub
    _results = None
    _lock = threading.Lock()

    def __init__(self, key):
        # Save the key
        GeniusUtility._headers = {'Authorization': 'Bearer ' +
                                  key, 'Content-Type': 'application/json'}
        GeniusUtility._t = threading.Thread(target=self.Polling, name="t1")
        GeniusUtility._t.daemon = True
        GeniusUtility._t.start()

    def _getjson(self, identifier):
        ''' gets the json from the supplied zone identifier '''
        url = GeniusUtility.HG_URL + identifier
        try:
            response = requests.get(url, headers=GeniusUtility._headers)

            if response.status_code == 200:
                results = json.loads(response.text)
                with GeniusUtility._lock:
                    GeniusUtility._results = results

        except Exception as ex:
            print("Failed requests in _getjson")
            print(ex)
            return None

    def Polling(self):
        while True:
            self._getjson('/zones')
            time.sleep(GeniusUtility.UPDATE_INTERVAL)

    def getZone(self, zoneId):
        results = self.getAllZones()
        for item in results:
            if item['id'] == zoneId:
                return item

        return None

    def getAllZones(self):
        results = None
        with GeniusUtility._lock:
            results = GeniusUtility._results

        return results

    def putjson(self, identifier, data):
        ''' puts the json data to the supplied zone identifier '''
        url = GeniusUtility.HG_URL + identifier
        try:
            response = requests.put(
                url, headers=GeniusUtility._headers, data=json.dumps(data))
            ''' refresh the results '''
            self._getjson('/zones')
            return response.status_code == 200

        except Exception as ex:
            print("Failed requests in putjson")
            print(ex)
            return False
