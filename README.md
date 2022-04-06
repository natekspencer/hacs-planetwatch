![](https://img.shields.io/github/v/release/natekspencer/hacs-planetwatch?style=for-the-badge)
[![Ko-Fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/natekspencer)

![](logo.png)

# PlanetWatch for Home Assistant

Home Assistant integration to update Awair sensor data in PlanetWatch.

You will also want to add the [official Home Assistant Awair integration](https://www.home-assistant.io/integrations/awair/), since that takes care of updating your Awair device data in Home Assistant. Installing this integration alone will simply show you the list of sensor ids associated with your PlanetWatch account. When both are installed, this integration taps into the data retrieval and then updates your sensors on PlanetWatch.

# Installation

There are two main ways to install this custom component within your Home Assistant instance:

1. Using HACS (see https://hacs.xyz/ for installation instructions if you do not already have it installed):

   1. From within Home Assistant, click on the link to **HACS**
   2. Click on **Integrations**
   3. Click on the vertical ellipsis in the top right and select **Custom repositories**
   4. Enter the URL for this repository in the section that says _Add custom repository URL_ and select **Integration** in the _Category_ dropdown list
   5. Click the **ADD** button
   6. Close the _Custom repositories_ window
   7. You should now be able to see the _PlanetWatch_ card on the HACS Integrations page. Click on **INSTALL** and proceed with the installation instructions.
   8. Restart your Home Assistant instance and then proceed to the _Configuration_ section below.

2. Manual Installation:
   1. Download or clone this repository
   2. Copy the contents of the folder **custom_components/planetwatch** into the same file structure on your Home Assistant instance
      - An easy way to do this is using the [Samba add-on](https://www.home-assistant.io/getting-started/configuration/#editing-configuration-via-sambawindows-networking), but feel free to do so however you want
   3. Restart your Home Assistant instance and then proceed to the _Configuration_ section below.

While the manual installation above seems like less steps, it's important to note that you will not be able to see updates to this custom component unless you are subscribed to the watch list. You will then have to repeat each step in the process. By using HACS, you'll be able to see that an update is available and easily update the custom component.

# Configuration

There is a config flow for this PlanetWatch integration. After installing the custom component, simply click the **ADD INTEGRATION** badge below

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=planetwatch)

_or_

1. Go to **Configuration**->**Integrations**
2. Click **+ ADD INTEGRATION** to setup a new integration
3. Search for **PlanetWatch** and click on it
4. You will be guided through the rest of the setup process via the config flow

---

## Support Me

I'm not employed by PlanetWatch or Awair, and provide this custom component purely for your own enjoyment and home automation needs.

If you find this integration useful and want to donate, consider buying me a coffee ☕ (or beer 🍺) by using the link below:

<a href='https://ko-fi.com/natekspencer' target='_blank'><img height='35' style='border:0px;height:46px;' src='https://az743702.vo.msecnd.net/cdn/kofi3.png?v=0' border='0' alt='Buy Me a Coffee at ko-fi.com' />
