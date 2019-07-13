# PLEASE NOTE

Genius Hub is now officially supported by **Home Assistant** (from v0.92), and this code is currently not maintained.
 - see: https://www.home-assistant.io/components/geniushub

# Genius Hub Component (Platform) for Home Assistant

Note: requires HA v0.89 or later.

Here's an integration of Genius Hub (HeatGenius) with Home Assistant (HASS). 
I have reverted to using the non-public API. This is because I would prefer to talk directly to the hub which is both faster and available when I have an internet outage. This also means, after a firmware update on the hub this component may fail as it did in an earlier version.

Climate supports controlling the heatings
Switch supports controlling the switches
Sensor reports battery, motion, luminance and temperature values from the sensor or batter and temperature values from the TRV valves.

## Installation
### Adding the Genius Hub Component to Home Assistant
The **genius.py** files need to be placed in the installation directory of Home Assistant. For me this is
```
<config_dir>/custom_components/geniushub/__init__.py
<config_dir>/custom_components/geniushub/climate.py
<config_dir>/custom_components/geniushub/sensor.py
<config_dir>/custom_components/geniushub/switch.py
``` 
There are instructions to follow on the instructions on the home-assistant website. If you need help, let me know.

### Adding Genius Hub to your configuration file
Now that the component is installed you will need to add the setup to you configuration file.

```
geniushub:
  username: !secret user_name
  password: !secret keep_this_secret
  host: local_ip_address
  scan_interval: seconds

```
**username** is mandatory and is the username required to log into your Genius Hub

**password** is mandatory and is the password required to log into your Genius Hub

**host** is mandatory and is the local ip address to Genius Hub e.g. 192.168.1.2

**scan_interval** is optional. If missing the default scan_interval is 6 seconds between polling the hub for an update


## More information
More information about the Genius Hub can be found here: https://www.geniushub.co.uk/

## TO DO
1. Create docker installer

Feel free to fork, help and improve
