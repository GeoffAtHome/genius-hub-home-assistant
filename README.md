# Genius Hub Component (Platform) for Home Assistant
Here's an integration of Genius Hub (HeatGenius) with Home Assistant (HASS). 
I have reverted to using the non-public API. This is because I would prefer to talk directly to the hub which is both faster and available when I have an internet outage. This also means, after a firmware update on the hub this component may fail as it did in an earlier version.

It works for reading the temperature from the Genius Hub. Support for switches is included. It does not currently support motion, luminance or setting of temperature or changing any setting in the hub.

## Installation
### Adding the Genius Hub Component to Home Assistant
The **genius.py** files need to be placed in the installation directory of Home Assistant. For me this is
```
/custom_components/climate/genius.py
/custom_components/switch/genius.py
/custom_components/genius.py
``` 
There are instructions to follow on the instructions on the home-assistant website. If you need help, let me know.

### Adding Genius Hub to your configuration file
Now that the component is installed you will need to add the setup to you configuration file.

```
genius:
  username: user_name
  password: keep_this_secret
  host: local_ip_address
  scan_interval: seconds

climate:
  - platform: genius

switch:
  - platform: genius
   
```
**username** is mandatory and is the username required to log into your Genius Hub

**password** is mandatory and is the password required to log into your Genius Hub

**host** is mandatory and is the local ip address to Genius Hub e.g. 192.168.1.2

**scan_interval** is optional. If missing the default scan_interval is 6 seconds between polling the hub for an update


## More information
More information about the Genius Hub can be found here: https://www.geniushub.co.uk/

## TO DO
1. Resolve issues in climate for switch between off, timer, boost and footprint so this works with Alexa
2. Resolve changes to setpoint temperates received from hass
3. Create docker installer

Feel free to fork, help and improve
