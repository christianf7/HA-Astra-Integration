import logging
from typing import Any
from homeassistant.core import callback
from homeassistant.core import HomeAssistant
from homeassistant.components.switch import SwitchEntity
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
    state = coordinator.data["channels"]["2"]["mode"]
    status = False
    if state == 2:
        status = True

    bstate = coordinator.data["channels"]["4"]["mode"]
    bstatus = False
    if bstate == 2:
        bstatus = True

    async_add_entities(
        [
            SpaJets(status, bridge, hass, coordinator),
            Blower(bstatus, bridge, hass, coordinator),
        ]
    )


class SpaJets(CoordinatorEntity, SwitchEntity):
    _attr_has_entity_name = True

    def __init__(self, state, hub, hass: HomeAssistant, coordinator) -> None:
        super().__init__(coordinator)
        self._is_on = state
        self._attr_unique_id = "astra_spa_jets"
        self._attr_name = f"Astra Spa Jets"
        self.hub = hub
        self.coordinator = coordinator
        self.hass = hass
        _LOGGER.debug(f"[ASTRA] {self._attr_unique_id} was registred in state: {state}")

    @property
    def is_on(self) -> bool:
        return self._is_on

    @callback
    def _handle_coordinator_update(self) -> None:
        state = self.coordinator.data["channels"]["2"]["mode"]
        status = False
        if state == 2:
            status = True
        self._is_on = status
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        self._is_on = False
        self.hass.async_add_executor_job(
            self.hub.set_status, 2, 1, "na", True, self.coordinator
        )

    async def async_turn_on(self, **kwargs):
        self._is_on = True
        self.hass.async_add_executor_job(
            self.hub.set_status, 2, 1, "na", True, self.coordinator
        )


class Blower(CoordinatorEntity, SwitchEntity):
    _attr_has_entity_name = True

    def __init__(self, state, hub, hass: HomeAssistant, coordinator) -> None:
        super().__init__(coordinator)
        self._is_on = state
        self._attr_unique_id = "astra_blower_jets"
        self._attr_name = f"Astra Blower"
        self.hub = hub
        self.coordinator = coordinator
        self.hass = hass
        _LOGGER.debug(f"[ASTRA] {self._attr_unique_id} was registred in state: {state}")

    @property
    def is_on(self) -> bool:
        return self._is_on

    @callback
    def _handle_coordinator_update(self) -> None:
        state = self.coordinator.data["channels"]["4"]["mode"]
        status = False
        if state == 2:
            status = True
        self._is_on = status
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        self._is_on = False
        self.hass.async_add_executor_job(
            self.hub.set_status, 4, 1, "na", True, self.coordinator
        )

    async def async_turn_on(self, **kwargs):
        self._is_on = True
        self.hass.async_add_executor_job(
            self.hub.set_status, 4, 1, "na", True, self.coordinator
        )
