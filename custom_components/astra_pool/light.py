import logging
from typing import Any
from homeassistant.core import callback
from homeassistant.core import HomeAssistant
from homeassistant.components.light import LightEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import BasicHub
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass,
    config_entry,
    async_add_entities,
) -> None:
    bridge: BasicHub = hass.data[DOMAIN][config_entry.entry_id]
    coordinator = hass.data[DOMAIN][config_entry.entry_id + "coordinator"]

    status = False
    if coordinator.data["lighting"]["mode"] == 2:
        status = True

    async_add_entities([PoolLight(status, bridge, hass, coordinator)])


class PoolLight(CoordinatorEntity, LightEntity):
    _attr_has_entity_name = True

    def __init__(self, state, hub, hass: HomeAssistant, coordinator) -> None:
        super().__init__(coordinator)
        self._is_on = state
        self._attr_unique_id = "astra_pool_lights"
        self._attr_name = f"Astra Pool Lights"
        self.hub = hub
        self.coordinator = coordinator
        self.hass = hass
        _LOGGER.debug(f"[ASTRA] {self._attr_unique_id} was registred in state: {state}")

    @property
    def name(self) -> str:
        return self._attr_name

    @property
    def is_on(self) -> bool:
        return self._is_on

    @callback
    def _handle_coordinator_update(self) -> None:
        state = self.coordinator.data["lighting"]["mode"]
        status = False
        if state == 2:
            status = True
        self._is_on = status
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        self._is_on = False
        self.hass.async_add_executor_job(
            self.hub.set_status, 0, 6, 0, True, self.coordinator
        )
        # await self.coordinator.async_request_refresh()

    async def async_turn_on(self, **kwargs):
        self._is_on = True
        self.hass.async_add_executor_job(
            self.hub.set_status, 0, 6, 2, True, self.coordinator
        )
        # await self.coordinator.async_request_refresh()
