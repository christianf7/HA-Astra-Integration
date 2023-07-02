import asyncio
import logging
from typing import Any
from homeassistant.core import callback
from homeassistant.core import HomeAssistant
from homeassistant.components.select import SelectEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .hub import BasicHub
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass,
    config_entry,
    async_add_entities,
) -> None:
    bridge: BasicHub = hass.data[DOMAIN][config_entry.entry_id]
    coordinator = hass.data[DOMAIN][config_entry.entry_id + "coordinator"]

    pool_mode = "Spa"
    if coordinator.data["pool"] == True:
        pool_mode = "Pool"

    async_add_entities(
        [
            SelectPumpMode(
                coordinator.data["channels"]["0"]["friendly"], bridge, hass, coordinator
            ),
            SelectSpillwayMode(
                coordinator.data["channels"]["1"]["friendly"], bridge, hass, coordinator
            ),
            SelectPoolMode(pool_mode, bridge, hass, coordinator),
        ]
    )


class SelectPoolMode(SelectEntity, CoordinatorEntity):
    _attr_options = ["Pool", "Spa"]
    _attr_unique_id = "astra_pool_mode"

    def __init__(self, pool_mode, hub, hass, coordinator):
        super().__init__(coordinator)  # Subscribe to polling events
        self._attr_current_option = pool_mode
        self.hub = hub
        self.hass = hass
        self.coordinator = coordinator

    @callback
    def _handle_coordinator_update(self) -> None:
        mode = "Spa"
        if self.coordinator.data["pool"] is True:
            mode = "Pool"

        self._attr_current_option = mode
        self.async_write_ha_state()

    async def async_select_option(self, option: str) -> None:
        self._attr_current_option = option
        if option.lower() == "spa":
            _LOGGER.warning("Setting astra mode to SPA")
            await self.hass.async_add_executor_job(
                self.hub.set_status, 1, 3, 0, True, self.coordinator
            )
        else:
            _LOGGER.warning("Setting astra mode to POOL")
            await self.hass.async_add_executor_job(
                self.hub.set_status, 1, 3, 1, True, self.coordinator
            )
            _LOGGER.warning("Setting pump & spillway status to AUTO")
            await asyncio.gather(
                self.hass.async_add_executor_job(
                    self.hub.set_status, 0, 1, "na", True, self.coordinator
                ),
                self.hass.async_add_executor_job(
                    self.hub.set_status, 1, 1, "na", True, self.coordinator
                ),
            )
        _LOGGER.info("Pool status successfully set as " + option + ".")


class SelectSpillwayMode(SelectEntity, CoordinatorEntity):
    _attr_options = ["Off", "Auto", "On"]
    _attr_unique_id = "astra_spillway_mode"

    def __init__(self, pump_mode, hub, hass, coordinator):
        super().__init__(coordinator)  # Subscribe to polling events
        self._attr_current_option = pump_mode
        self.hub = hub
        self.hass = hass
        self.coordinator = coordinator

    @callback
    def _handle_coordinator_update(self) -> None:
        self._attr_current_option = self.coordinator.data["channels"]["1"]["friendly"]
        self.async_write_ha_state()

    async def async_select_option(self, option: str) -> None:
        ol_option = self._attr_current_option
        self._attr_current_option = option

        match option.lower():
            case "off":
                iterations = {"Auto": 2, "On": 1}.get(ol_option, 0)

                for _ in range(iterations - 1):
                    await self.hass.async_add_executor_job(
                        self.hub.set_status, 1, 1, "na"
                    )
                await self.hass.async_add_executor_job(
                    self.hub.set_status, 1, 1, "na", True, self.coordinator
                )
                _LOGGER.warning("Setting astra spillway mode to Off")
            case "auto":
                iterations = {"Off": 1, "On": 2}.get(ol_option, 0)

                for _ in range(iterations - 1):
                    await self.hass.async_add_executor_job(
                        self.hub.set_status, 1, 1, "na"
                    )
                await self.hass.async_add_executor_job(
                    self.hub.set_status, 1, 1, "na", True, self.coordinator
                )
                _LOGGER.warning("Setting astra spillway mode to auto")
            case "on":
                iterations = {
                    "Off": 1,
                    "Auto": 2,
                }.get(ol_option, 0)

                for _ in range(iterations - 1):
                    await self.hass.async_add_executor_job(
                        self.hub.set_status, 1, 1, "na"
                    )
                await self.hass.async_add_executor_job(
                    self.hub.set_status, 1, 1, "na", True, self.coordinator
                )
                _LOGGER.warning("Setting astra spillway mode to on")
            case _:
                _LOGGER.error("Could not determine mode when setting spillway")
        _LOGGER.info("Pool status successfully set as " + option + ".")


class SelectPumpMode(SelectEntity, CoordinatorEntity):
    _attr_options = ["Off", "Auto", "Medium", "High"]
    _attr_unique_id = "astra_pump_mode"

    def __init__(self, pump_mode, hub, hass, coordinator):
        super().__init__(coordinator)  # Subscribe to polling events
        self._attr_current_option = pump_mode
        self.hub = hub
        self.hass = hass
        self.coordinator = coordinator

    @callback
    def _handle_coordinator_update(self) -> None:
        self._attr_current_option = self.coordinator.data["channels"]["0"]["friendly"]
        self.async_write_ha_state()

    async def async_select_option(self, option: str) -> None:
        ol_option = self._attr_current_option
        self._attr_current_option = option

        match option.lower():
            case "off":
                iterations = {"Auto": 3, "Medium": 2, "High": 1}.get(ol_option, 0)

                for _ in range(iterations - 1):
                    await self.hass.async_add_executor_job(
                        self.hub.set_status, 0, 1, "na"
                    )
                await self.hass.async_add_executor_job(
                    self.hub.set_status, 0, 1, "na", True, self.coordinator
                )
                _LOGGER.warning("Setting astra pump mode to Off")
            case "auto":
                iterations = {"Off": 1, "Medium": 3, "High": 2}.get(ol_option, 0)

                for _ in range(iterations - 1):
                    await self.hass.async_add_executor_job(
                        self.hub.set_status, 0, 1, "na"
                    )
                await self.hass.async_add_executor_job(
                    self.hub.set_status, 0, 1, "na", True, self.coordinator
                )
                _LOGGER.warning("Setting astra pump mode to Auto")
            case "medium":
                iterations = {"Auto": 1, "Off": 2, "High": 3}.get(ol_option, 0)

                for _ in range(iterations - 1):
                    await self.hass.async_add_executor_job(
                        self.hub.set_status, 0, 1, "na"
                    )
                await self.hass.async_add_executor_job(
                    self.hub.set_status, 0, 1, "na", True, self.coordinator
                )
                _LOGGER.warning("Setting astra pump mode to Medium")
            case "high":
                iterations = {"Auto": 2, "Medium": 1, "Off": 3}.get(ol_option, 0)

                for _ in range(iterations - 1):
                    await self.hass.async_add_executor_job(
                        self.hub.set_status, 0, 1, "na"
                    )

                await self.hass.async_add_executor_job(
                    self.hub.set_status, 0, 1, "na", True, self.coordinator
                )

                _LOGGER.warning("Setting astra pump mode to High")
            case _:
                _LOGGER.error("Could not determine mode when setting pump.")
        _LOGGER.info("Pool status successfully set as " + option + ".")
