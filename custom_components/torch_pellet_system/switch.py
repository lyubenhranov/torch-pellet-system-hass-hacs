"""Support for setting the Deluge BitTorrent client in Pause."""
from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_platform

from . import TorchPelletSystemEntity
from .const import *
from .coordinator import TorchPelletSystemDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: entity_platform.AddEntitiesCallback,
) -> None:
    """Set up the Torch Pellet System switches."""

    async_add_entities(
        [
            TorchPelletSystemSwitch(
                hass.data[DOMAIN][entry.entry_id], "Torch Pellet System State"
            )
        ]
    )


class TorchPelletSystemSwitch(TorchPelletSystemEntity, SwitchEntity):
    """Representation of a Torch Pellet System switch."""

    def __init__(
        self, coordinator: TorchPelletSystemDataUpdateCoordinator, switch_name
    ) -> None:
        """Initialize the Torch Pellet System switch."""

        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_enabled"
        self._attr_name = switch_name

    def turn_on(self, **kwargs: Any) -> None:
        """Turn the Torch Pellet System on."""

        self.coordinator.api.turn_burner_on()

    def turn_off(self, **kwargs: Any) -> None:
        """Turn the Torch Pellet System off."""

        self.coordinator.api.turn_burner_off()

    @property
    def is_on(self) -> bool:
        """Return state of the Torch Pellet System switch."""

        if self.coordinator.data:
            pellet_system_state = self.coordinator.data[Platform.SWITCH][
                PELLET_SYSTEM_STATE_KEY
            ]

            if pellet_system_state == 0:
                return False
            else:
                return True

        return False
