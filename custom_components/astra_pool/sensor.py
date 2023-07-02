import logging
from typing import Any
from homeassistant.core import callback
from homeassistant.core import HomeAssistant
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .hub import BasicHub, PHCoordinator
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass,
    config_entry,
    async_add_entities,
) -> None:
    bridge: BasicHub = hass.data[DOMAIN][config_entry.entry_id]
    coordinator = hass.data[DOMAIN][config_entry.entry_id + "coordinator"]
    phcoordinator = PHCoordinator(hass, bridge)
    await phcoordinator.async_config_entry_first_refresh()
    async_add_entities(
        [
            PoolTemperature(coordinator.data["temperature"], coordinator),
            SetPoolTemperature(coordinator.data["heater"]["temperature"], coordinator),
            SetSpaTemperature(coordinator.data["heater"]["spa_temperature"], coordinator),
            PHValue(phcoordinator.data["ph"], phcoordinator),
        ]
    )

class PoolTemperature(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True
    _attr_unit_of_measurement = "temperature"

    def __init__(self, state, coordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = "astra_pool_temperature"
        self._attr_name = f"Astra Pool Temperature"
        self._attr_state = state
        _LOGGER.debug(f"[ASTRA] {self._attr_unique_id} was registred in state: {state}")

    @callback
    def _handle_coordinator_update(self) -> None:
        state = self.coordinator.data["temperature"]
        self._attr_state = state
        self.async_write_ha_state()

    @property
    def state(self):
        return self._attr_state


class SetPoolTemperature(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True
    _attr_unit_of_measurement = "temperature"

    def __init__(self, state, coordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = "astra_pool_set_temperature"
        self._attr_name = f"Astra Pool Set Temperature"
        self._attr_state = state
        _LOGGER.debug(f"[ASTRA] {self._attr_unique_id} was registred in state: {state}")

    @callback
    def _handle_coordinator_update(self) -> None:
        state = self.coordinator.data["heater"]["temperature"]
        self._attr_state = state
        self.async_write_ha_state()

    @property
    def state(self):
        return self._attr_state


class SetSpaTemperature(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True
    _attr_unit_of_measurement = "temperature"

    def __init__(self, state, coordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = "astra_spa_set_temperature"
        self._attr_name = f"Astra Spa Set Temperature"
        self._attr_state = state
        _LOGGER.debug(f"[ASTRA] {self._attr_unique_id} was registred in state: {state}")

    @callback
    def _handle_coordinator_update(self) -> None:
        state = self.coordinator.data["heater"]["spa_temperature"]
        self._attr_state = state
        self.async_write_ha_state()

    @property
    def state(self):
        return self._attr_state


class PHValue(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True
    _attr_unit_of_measurement = "temperature"

    def __init__(self, state, coordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = "astra_pool_ph"
        self._attr_name = f"Astra Pool PH"
        self._attr_state = state
        _LOGGER.debug(f"[ASTRA] {self._attr_unique_id} was registred in state: {state}")

    @callback
    def _handle_coordinator_update(self) -> None:
        state = self.coordinator.data["ph"]
        self._attr_state = state
        self.async_write_ha_state()

    @property
    def state(self):
        return self._attr_state
