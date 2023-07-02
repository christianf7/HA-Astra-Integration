import asyncio
from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature as f,
    HVACMode as m,
    UnitOfTemperature as t,
)
import logging

from homeassistant.core import callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from . import DOMAIN
from .hub import BasicHub

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass,
    config_entry,
    async_add_entities,
) -> None:
    bridge: BasicHub = hass.data[DOMAIN][config_entry.entry_id]
    coord = hass.data[DOMAIN][config_entry.entry_id + "coordinator"]
    coordinator = coord.data

    mode = "Spa"
    stat = "heat"
    max_temp = coordinator["heater"]["spa_temperature"]

    if coordinator["pool"] is True:
        mode = "Pool"
        max_temp = coordinator["heater"]["temperature"]

    if coordinator["heater"]["mode"] == 0:
        stat = "off"

    async_add_entities(
        [PoolHeater(coordinator["temperature"], max_temp, stat, mode, coord, bridge)]
    )


class PoolHeater(ClimateEntity, CoordinatorEntity):
    _attr_supported_features = f.TARGET_TEMPERATURE | f.PRESET_MODE
    _attr_unique_id = "astra_pool_heater"
    _attr_preset_modes = ["Spa", "Pool"]
    _attr_temperature_unit = t.CELSIUS
    _attr_hvac_modes = [m.OFF, m.HEAT]
    _attr_target_temperature_high = 22
    _attr_target_temperature_low = 22
    _attr_name = "Astra Pool Heater"
    _attr_has_entity_name = True
    _attr_max_temp = 40
    _attr_target_temperature_step = 1
    _attr_min_temp = 22

    def __init__(self, temp, set_temp, state, mode, coordinator, hub) -> None:
        super().__init__(coordinator)  # Subscribe to polling events

        self._attr_target_temperature = set_temp
        self._attr_current_temperature = temp
        self._attr_preset_mode = mode
        self._attr_hvac_mode = state
        self.coordinator = coordinator
        self.hub = hub

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return DeviceInfo(
            identifiers={
                # Serial numbers are unique identifiers within a specific domain
                (DOMAIN, self.unique_id)
            },
            name=self.name,
            manufacturer="Astra Pools",
            model="Connect 10",
            sw_version="1.0.0",
            via_device=(DOMAIN, "POOL"),
        )

    @callback
    def _handle_coordinator_update(self) -> None:
        mode = "Spa"
        stat = "heat"
        max_temp = self.coordinator.data["heater"]["spa_temperature"]

        if self.coordinator.data["pool"] is True:
            mode = "Pool"
            max_temp = self.coordinator.data["heater"]["temperature"]

        if self.coordinator.data["heater"]["mode"] == 0:
            stat = "off"

        self._attr_current_temperature = self.coordinator.data["temperature"]
        self._attr_target_temperature = max_temp
        self._attr_hvac_mode = stat
        self._attr_preset_mode = mode

        self.async_write_ha_state()

    async def async_set_hvac_mode(self, hvac_mode):
        self._attr_hvac_mode = hvac_mode
        _LOGGER.warning("Setting heater to " + hvac_mode + ".")
        if hvac_mode == "heat":
            await asyncio.gather(
                self.hass.async_add_executor_job(self.hub.set_status, 1, 4, 1, True, self.coordinator),
                self.hass.async_add_executor_job(self.hub.set_status, 0, 2, 2, True, self.coordinator)
            )
        else:
            await asyncio.gather(
                self.hass.async_add_executor_job(self.hub.set_status, 1, 4, 0, True, self.coordinator),
                self.hass.async_add_executor_job(self.hub.set_status, 0, 2, 0, True, self.coordinator)
            )
        _LOGGER.info("Successfully turned heater to " + hvac_mode + ".")

    async def async_set_temperature(self, **kwargs):
        temp = kwargs.get("temperature")
        self._attr_target_temperature = temp
        _LOGGER.warning("Setting heating temperature to " + str(temp))
        await self.hass.async_add_executor_job(
            self.hub.set_status, 1, 5, int(temp), True, self.coordinator
        )
        _LOGGER.info("Set heating temperature to " + str(temp))

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        self._attr_preset_mode = preset_mode
        if preset_mode.lower() == "spa":
            _LOGGER.warning("Setting astra mode to SPA")
            await self.hass.async_add_executor_job(self.hub.set_status, 1, 3, 0, True, self.coordinator)
        else:
            _LOGGER.warning("Setting astra mode to POOL")
            await self.hass.async_add_executor_job(self.hub.set_status, 1, 3, 1, True, self.coordinator)
            _LOGGER.warning("Setting pump & spillway status to AUTO")
            await asyncio.gather(
                self.hass.async_add_executor_job(self.hub.set_status, 0, 1, "na", True, self.coordinator),
                self.hass.async_add_executor_job(self.hub.set_status, 1, 1, "na", True, self.coordinator),
            )
        _LOGGER.info("Pool status successfully set as " + preset_mode + ".")
