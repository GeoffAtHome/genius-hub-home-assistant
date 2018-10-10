
''' This module contains utility functions that are shared across other programs '''
import json
import aiohttp
import asyncio
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
    api_key = config[DOMAIN].get(CONF_API_KEY)
    hass.data[GENIUS_LINK] = GeniusUtility(api_key)
    return True


class GeniusUtility():
    HG_URL = "https://my.geniushub.co.uk/v1"
    UPDATE_INTERVAL = 5  # Interval between fetching new data from the Genius hub
    _results = []

    def __init__(self, key):
        # Save the key
        GeniusUtility._headers = {'Authorization': 'Bearer ' +
                                  key, 'Content-Type': 'application/json'}

        GeniusUtility._t = threading.Thread(
            target=self.StartPolling, name="t1")
        GeniusUtility._t.daemon = True
        GeniusUtility._t.start()

    async def fetch(self, session, url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=GeniusUtility._headers) as response:
                return await response.text()

    async def getjson(self, identifier):
        ''' gets the json from the supplied zone identifier '''
        url = GeniusUtility.HG_URL + identifier
        try:
            async with aiohttp.ClientSession() as session:
                text = await self.fetch(session, url)

                GeniusUtility._results = json.loads(text)

        except Exception as ex:
            _LOGGER.info("Failed requests in getjson")
            _LOGGER.info(ex)
            return None

    def StartPolling(self):
        loop = asyncio.new_event_loop()
        loop.run_until_complete(self.Polling())

    async def Polling(self):
        while True:
            await self.getjson('/zones')
            print("Sleeping")
            await asyncio.sleep(GeniusUtility.UPDATE_INTERVAL)

    def getZone(self, zoneId):
        for item in GeniusUtility._results:
            if item['id'] == zoneId:
                return item

        return None

    def getAllZones(self):
        return GeniusUtility._results

    async def place(self, session, url, data):
        async with aiohttp.ClientSession() as session:
            async with session.put(url, headers=GeniusUtility._headers, data=json.dumps(data)) as response:
                assert response.status == 200

    async def putjson(self, device_id, identifier, data):
        ''' puts the json data to the supplied zone identifier '''
        url = GeniusUtility.HG_URL + '/zones/' + str(device_id) + identifier
        try:
            async with aiohttp.ClientSession() as session:
                status = await self.place(session, url, data)

            ''' refresh the results '''
            await self.getjson('/zones')
            return status == 200

        except Exception as ex:
            _LOGGER.info("Failed requests in putjson")
            _LOGGER.info(ex)
            return False
