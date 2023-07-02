import requests
from typing import Any
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
)
from datetime import timedelta

from .const import DOMAIN
import logging

_LOGGER = logging.getLogger(__name__)


class BasicHub:
    def __init__(self, host: str, hass="na") -> None:
        self.host = host
        self.hass = hass
        self.actions = 0

    def verify_connection(self):
        try:
            r = requests.get(f"http://{self.host}/verify", timeout=10000)
            _LOGGER.info("Verified connection to AstraPool.")
            return r.status_code == 200
        except:
            return False

    def get_status(self):
        r = requests.get(f"http://{self.host}/status", timeout=10000)
        return r.json()

    def get_ph(self):
        r = requests.get(f"http://{self.host}/chemistry", timeout=10000)
        return r.json()

    def get_light(self):
        r = requests.get(f"http://{self.host}/status/lighting", timeout=10000)
        return r.json()

    def set_status(self, device, action, value, wait=False, coordinator=False):
        self.actions = self.actions + 1
        self.hass.states.set("binary_sensor.astra_pool_loading", "on")
        r = requests.get(
            f"http://{self.host}/set/{device}/{action}/{value}?wait={wait}",
            timeout=60000,
        )

        if coordinator != False:
            coordinator.async_request_refresh()

        self.actions = self.actions - 1
        if self.actions == 0:
            self.hass.states.set("binary_sensor.astra_pool_loading", "off")
        return r.json()


class MyCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, my_api) -> None:
        self.hass = hass
        super().__init__(
            hass,
            _LOGGER,
            name="Astra Polling",
            update_interval=timedelta(seconds=3),
        )
        self.my_api = my_api

    async def _async_update_data(self):
        stat = await self.hass.async_add_executor_job(self.my_api.get_status)
        return stat


class PHCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, my_api) -> None:
        self.hass = hass
        super().__init__(
            hass,
            _LOGGER,
            name="Astra PH Polling",
            update_interval=timedelta(seconds=10),
        )
        self.my_api = my_api

    async def _async_update_data(self):
        stat = await self.hass.async_add_executor_job(self.my_api.get_ph)
        return stat
