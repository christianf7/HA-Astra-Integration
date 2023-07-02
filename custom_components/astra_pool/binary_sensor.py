import logging
from typing import Any
from homeassistant.core import callback
from homeassistant.core import HomeAssistant
from homeassistant.components.binary_sensor import BinarySensorEntity
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
    hass.data[DOMAIN][config_entry.entry_id + "loading"] = False

    async_add_entities([IsLoading(False, bridge, hass, coordinator, config_entry)])


class IsLoading(BinarySensorEntity):
    _attr_has_entity_name = True

    def __init__(
        self, state, hub, hass: HomeAssistant, coordinator, config_entry
    ) -> None:
        # super().__init__(coordinator)
        self._is_on = state
        self._attr_unique_id = "astra_pool_loading"
        self._attr_name = f"Astra Pool Loading"
        self.hub = hub
        self.hass = hass
        self.config_entry = config_entry
        _LOGGER.debug(f"[ASTRA] {self._attr_unique_id} was registred in state: {state}")

    @property
    def is_on(self) -> bool:
        return self.hass.data[DOMAIN][self.config_entry.entry_id + "loading"]