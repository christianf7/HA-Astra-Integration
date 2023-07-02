"""The Kasta-Slowfind integration."""
from __future__ import annotations
from .hub import BasicHub, MyCoordinator

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

import requests

from .const import DOMAIN
from .config_flow import CannotConnect

# TODO List the platforms that you want to support.
# For your initial PR, limit it to 1 platform.
PLATFORMS: list[Platform] = [
    Platform.LIGHT,
    Platform.SENSOR,
    Platform.CLIMATE,
    Platform.SELECT,
    Platform.BINARY_SENSOR,
    Platform.SWITCH,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Kasta-Slowfind from a config entry."""

    hass.data.setdefault(DOMAIN, {})
    # TODO 1. Create API instance
    # TODO 2. Validate the API connection (and authentication)
    # TODO 3. Store an API object for your platforms to access
    hub = BasicHub(entry.data["host"], hass)
    hass.data[DOMAIN][entry.entry_id] = hub

    connection = await hass.async_add_executor_job(hub.verify_connection)
    if connection == False:
        raise CannotConnect

    coordinator = MyCoordinator(hass, hub)
    await coordinator.async_config_entry_first_refresh()
    hass.data[DOMAIN][entry.entry_id + "coordinator"] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
