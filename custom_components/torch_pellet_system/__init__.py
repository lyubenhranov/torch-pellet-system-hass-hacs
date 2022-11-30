"""The Torch Pellet System integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

from .torch_api import TorchApi
from .coordinator import TorchPelletSystemDataUpdateCoordinator

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.SWITCH]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Torch Pellet System from a config entry."""

    api = await hass.async_add_executor_job(
        TorchApi, entry.data["username"], entry.data["password"]
    )

    coordinator = TorchPelletSystemDataUpdateCoordinator(hass, api, entry)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


class TorchPelletSystemEntity(
    CoordinatorEntity[TorchPelletSystemDataUpdateCoordinator]
):
    """Representation of a Torch Pellet System entity."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: TorchPelletSystemDataUpdateCoordinator) -> None:
        """Initialize a Torch Pellet System entity."""

        super().__init__(coordinator)
        self._server_unique_id = coordinator.config_entry.entry_id
