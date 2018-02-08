# Genius Hub Component (Platform) for Home Assistant
Here's an integration of Genius Hub (HeatGenius) with Home Assistant (HASS).

It works for reading the temperature from the Genius Hub. It does not currently support switches, motion, luminance or setting of temperature or changing any setting in the hub.

## Installation
### Adding the Genius Hub Component to Home Assistant
The genius.py and utils.py files need to be placed in the installation directory of Home Assistant. For me this is
```
/custom_components/climate/
``` 
There are instructions to follow on the instructions on the home-assistant website. If you need help, let me know.

### Adding Genius Hub to your configuration file
Now that the component is installed you will need to add the setup to you configuration file.

```
climate:
  - platform: genius
    host: xx.yy.zz.aa
    api_key: keep_this_secret
   
```
Both **host** and **api_key** are mandatory. 
**host** is the url of your Genius Hub on your local network
**api_key** is the API Signature value that can be found in the Genius Hub UI on the about page.

## More information
More information about the Genius Hub can be found here: https://www.geniushub.co.uk/