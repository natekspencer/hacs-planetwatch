"""The PlanetWatch integration."""
from __future__ import annotations

from homeassistant.components.awair import (
    LOGGER,
    AwairDataUpdateCoordinator,
    AwairResult,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.config_entry_oauth2_flow import (
    OAuth2Session,
    async_get_config_entry_implementation,
)

from . import api, config_flow
from .const import DOMAIN, OAUTH2_AUTHORIZE, OAUTH2_CLIENTID, OAUTH2_TOKEN
from .pyplanetwatch import PlanetWatchApi

PLATFORMS: list[Platform] = [Platform.SENSOR]


_OLD_FETCH_AIR_DATA = AwairDataUpdateCoordinator._fetch_air_data


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up PlanetWatch from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    config_flow.OAuth2FlowHandler.async_register_implementation(
        hass,
        api.PlanetWatchLocalOAuth2Implementation(
            hass,
            DOMAIN,
            OAUTH2_CLIENTID,
            None,
            OAUTH2_AUTHORIZE,
            OAUTH2_TOKEN,
        ),
    )

    implementation = await async_get_config_entry_implementation(hass, entry)

    session = OAuth2Session(hass, entry, implementation)
    planetwatch_api = PlanetWatchApi(
        api.AsyncConfigEntryAuth(async_get_clientsession(hass), session)
    )

    async def _fetch_air_data_and_send_to_planetwatch(self, device):
        """Fetch latest air quality data."""
        # pylint: disable=no-self-use
        LOGGER.debug("Fetching data for %s", device.uuid)
        air_data = await device.air_data_latest()
        LOGGER.debug(air_data)
        hass.async_create_task(
            planetwatch_api.send_awair_sensor_data(device.uuid, air_data)
        )
        return AwairResult(device=device, air_data=air_data)

    AwairDataUpdateCoordinator._fetch_air_data = _fetch_air_data_and_send_to_planetwatch

    hass.data[DOMAIN][entry.entry_id] = planetwatch_api

    hass.config_entries.async_setup_platforms(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    AwairDataUpdateCoordinator._fetch_air_data = _OLD_FETCH_AIR_DATA

    return unload_ok
