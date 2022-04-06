"""Support for PlanetWatch sensors."""
from __future__ import annotations

from datetime import datetime

from homeassistant.components.sensor import RestoreSensor, SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .pyplanetwatch import UPDATE, PlanetWatchApi, Sensor


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up PlanetWatch sensor entity based on a config entry."""
    api: PlanetWatchApi = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities(
        [PlanetWatchSensor(sensor) for sensor in await api.get_sensors()]
    )


class PlanetWatchSensor(RestoreSensor):
    """Defines a PlanetWatch sensor entity."""

    def __init__(self, sensor: Sensor) -> None:
        """Set up an individual PlanetWatchSensor."""
        self._sensor = sensor
        self._attr_device_class = SensorDeviceClass.TIMESTAMP

    @property
    def name(self) -> str | None:
        """Return the name of the sensor."""
        return f"PlanetWatch Sensor: {self._sensor.sensor_id}"

    @property
    def unique_id(self) -> str:
        """Return the sensorId as the unique_id."""
        return f"{DOMAIN}_{self.name}"

    @property
    def native_value(self) -> datetime | None:
        """Return the native value of the sensor."""
        return self._sensor.last_updated

    async def async_added_to_hass(self) -> None:
        """Restore previous value."""
        if (previous_state := await self.async_get_last_sensor_data()) is not None:
            self._sensor.last_updated = previous_state.native_value
        self.async_on_remove(self._sensor.on(UPDATE, self.async_write_ha_state))
