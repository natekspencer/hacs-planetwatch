"""PlanetWatch python module."""
from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from collections.abc import Callable
from datetime import datetime, timedelta, timezone
from typing import Any

from aiohttp import ClientResponse, ClientSession
from python_awair.air_data import AirData
from python_awair.const import DATE_FORMAT, SENSOR_TO_ALIAS

API_ENDPOINT = "https://wearableapi.planetwatch.io/api"
MINIMUM_TIME_BETWEEN_UPDATES = timedelta(minutes=15)
UPDATE = "update"

_LOGGER = logging.getLogger(__name__)


class AbstractAuth(ABC):
    """Abstract class to make authenticated requests."""

    def __init__(self, websession: ClientSession) -> None:
        """Initialize the auth."""
        self.websession = websession

    @abstractmethod
    async def async_get_access_token(self) -> str:
        """Return a valid access token."""

    async def request(self, method, url, **kwargs) -> ClientResponse:
        """Make a request."""
        headers = kwargs.get("headers")

        if headers is None:
            headers = {}
        else:
            headers = dict(headers)

        access_token = await self.async_get_access_token()
        headers["authorization"] = f"Bearer {access_token}"

        return await self.websession.request(
            method,
            f"{API_ENDPOINT}/{url}",
            **kwargs,
            headers=headers,
        )


class Sensor:
    """Sensor."""

    def __init__(self, data: dict[str, str]) -> None:
        """Initialize a sensor."""
        self._data: dict[str, str] = data
        self._last_updated: datetime | None = None
        self._listeners: dict[str, list[Callable]] = {}

    @property
    def sensor_id(self) -> str:
        """Return the sensor id."""
        return self._data.get("sensorId")

    @property
    def last_updated(self) -> datetime | None:
        """Return the last updated datetime."""
        return self._last_updated

    @last_updated.setter
    def last_updated(self, value: datetime | None) -> None:
        """Set the last updated date of the sensor."""
        self._last_updated = value
        self.emit(UPDATE)

    def can_be_updated(self) -> bool:
        """Return if the sensor can be updated."""
        return (
            self._last_updated is None
            or self._last_updated + MINIMUM_TIME_BETWEEN_UPDATES
            <= datetime.now(timezone.utc)
        )

    def on(self, event_name: str, callback: Callable) -> Callable:
        """Register an event callback."""
        # pylint: disable=invalid-name
        listeners: list = self._listeners.setdefault(event_name, [])
        listeners.append(callback)

        def unsubscribe() -> None:
            """Unsubscribe listeners."""
            if callback in listeners:
                listeners.remove(callback)

        return unsubscribe

    def emit(self, event_name: str) -> None:
        """Run all callbacks for an event."""
        for listener in self._listeners.get(event_name, []):
            listener()


class PlanetWatchApi:
    """PlanetWatch API."""

    def __init__(self, auth: AbstractAuth) -> None:
        """Initialize the API."""
        self.auth = auth
        self.sensors: list[Sensor] = []

    async def get_sensors(self) -> list[Sensor]:
        """Get PlanetWatch sensors."""
        if not self.sensors:
            response = await self.auth.request("GET", "sensors")
            response.raise_for_status()
            if response.status == 200:
                self.sensors = [
                    Sensor(sensor_data)
                    for sensor_data in (await response.json()).get("data")
                ]
        return self.sensors

    async def send_awair_sensor_data(self, device_id: str, data: AirData) -> bool:
        """Update PlanetWatch sensor data."""
        if not data or not (
            sensor := next(
                (
                    sensor
                    for sensor in self.sensors
                    if sensor.sensor_id == device_id and sensor.can_be_updated()
                ),
                None,
            )
        ):
            return False
        updated_data = awair_air_data_as_dict(device_id, data)
        try:
            response = await self.auth.request(
                "POST", "data/devicedata", json=updated_data
            )
            response.raise_for_status()
            if response.status == 200:
                sensor.last_updated = datetime.now(timezone.utc)
                return True
            else:
                return False
        except Exception as ex:
            _LOGGER.error(ex)
            return False


ALIAS_TO_SENSOR = {v: k for k, v in SENSOR_TO_ALIAS.items()}


def awair_air_data_as_dict(
    device_id: str, data: AirData | None
) -> dict[str, Any] | None:
    """Convert Awair AirData to a dict."""
    if data is None:
        return None
    return {
        "deviceId": device_id,
        "timestamp": data.timestamp.strftime(DATE_FORMAT),
        "score": data.score,
        "sensors": [
            {"comp": ALIAS_TO_SENSOR.get(s, s), "value": v}
            for s, v in data.sensors.items()
        ],
        "indices": [
            {"comp": ALIAS_TO_SENSOR.get(s, s), "value": v}
            for s, v in data.indices.items()
        ],
    }
