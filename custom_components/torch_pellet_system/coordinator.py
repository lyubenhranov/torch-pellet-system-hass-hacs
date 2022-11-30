"""Data update coordinator for the Torch Pellet System integration."""
from __future__ import annotations

from datetime import timedelta
import socket
from ssl import SSLError

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import LOGGER

from .torch_api import TorchApi


class TorchPelletSystemDataUpdateCoordinator(DataUpdateCoordinator):
    """Data update coordinator for the Torch Pellet System integration."""

    config_entry: ConfigEntry

    def __init__(self, hass: HomeAssistant, api: TorchApi, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass=hass,
            logger=LOGGER,
            name=entry.title,
            update_interval=timedelta(seconds=30),
        )
        self.api = api
        self.config_entry = entry

    async def _async_update_data(self) -> dict[Platform, dict[str, int | str]]:
        """Get the latest data from Torch Pellet System API and update the state."""

        data = {}

        returned_data = await self.hass.async_add_executor_job(self.api.get_data)

        data[Platform.SENSOR] = returned_data
        data[Platform.SWITCH] = returned_data

        return data
