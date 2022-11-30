"""Support for monitoring the Torch Pellet System Sensors."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import *
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_platform
from homeassistant.helpers.typing import StateType

from . import TorchPelletSystemEntity
from .coordinator import TorchPelletSystemDataUpdateCoordinator

from .const import *


def get_state(data: dict[str, float], key: str) -> str | float:
    """Get current state of the Torch Pellet Sensor."""

    data_value = data[key]

    if key == PELLET_SYSTEM_STATE_KEY:
        if data_value == "0":
            return "Turned Off"
        if data_value == "1":
            return "Starting"
        if data_value == "3":
            return "Burning"
        if data_value == "4" or data_value == "5":
            return "Cooling Down"
        if data_value == "6":
            return "Waiting"

        return "Unknown State"

    if key == PELLET_SYSTEM_TNC_STATUS_KEY:
        if data_value == "0":
            return "Offline"
        if data_value == "1":
            return "Online"

        return "Unknown State"

    return data_value


@dataclass
class TorchPelletSystemSensorEntityDescription(SensorEntityDescription):
    """Class to describe a Torch Pellet System sensor."""

    value: Callable[[dict[str, float]], Any] = lambda val: val


SENSOR_TYPES: tuple[TorchPelletSystemSensorEntityDescription, ...] = (
    TorchPelletSystemSensorEntityDescription(
        key=PELLET_SYSTEM_STATE_KEY,
        name="Pellet System State",
        value=lambda data: get_state(data, PELLET_SYSTEM_STATE_KEY),
    ),
    TorchPelletSystemSensorEntityDescription(
        key=PELLET_SYSTEM_TNC_STATUS_KEY,
        name="Pellet System Torch Net Control State",
        value=lambda data: get_state(data, PELLET_SYSTEM_TNC_STATUS_KEY),
    ),
    TorchPelletSystemSensorEntityDescription(
        key=WATER_TEMPERATURE_SETTING_KEY,
        name="Water Temperature Setting",
        device_class=DEVICE_CLASS_TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        value=lambda data: get_state(data, WATER_TEMPERATURE_SETTING_KEY),
    ),
    TorchPelletSystemSensorEntityDescription(
        key=WATER_TEMPERATURE_OUT_OF_THE_PELLET_SYSTEM_KEY,
        name="Water Temperature Going out of the Pellet System",
        device_class=DEVICE_CLASS_TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        value=lambda data: get_state(
            data, WATER_TEMPERATURE_OUT_OF_THE_PELLET_SYSTEM_KEY
        ),
    ),
    TorchPelletSystemSensorEntityDescription(
        key=WATER_TEMPERATURE_COMING_IN_THE_PELLET_SYSTEM_KEY,
        name="Water Temperature Coming in the Pellet System",
        device_class=DEVICE_CLASS_TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        value=lambda data: get_state(
            data, WATER_TEMPERATURE_COMING_IN_THE_PELLET_SYSTEM_KEY
        ),
    ),
    TorchPelletSystemSensorEntityDescription(
        key=PELLET_BURNER_TEMPERATURE_KEY,
        name="Pellet Burner Temperature",
        device_class=DEVICE_CLASS_TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
        value=lambda data: get_state(data, PELLET_BURNER_TEMPERATURE_KEY),
    ),
    TorchPelletSystemSensorEntityDescription(
        key=LIGTH_SENSOR_KEY,
        name="Flame Light Sensor",
        device_class=DEVICE_CLASS_ILLUMINANCE,
        state_class=SensorStateClass.MEASUREMENT,
        value=lambda data: get_state(data, LIGTH_SENSOR_KEY),
    ),
    TorchPelletSystemSensorEntityDescription(
        key=BURNER_CURRENT_WORKING_POWER_KEY,
        name="Burner Current Working Power",
        device_class=DEVICE_CLASS_POWER,
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        state_class=SensorStateClass.MEASUREMENT,
        value=lambda data: get_state(data, BURNER_CURRENT_WORKING_POWER_KEY),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: entity_platform.AddEntitiesCallback,
) -> None:
    """Set up Torch Pellet System sensors."""

    async_add_entities(
        TorchPelletSystemSensor(hass.data[DOMAIN][entry.entry_id], description)
        for description in SENSOR_TYPES
    )


class TorchPelletSystemSensor(TorchPelletSystemEntity, SensorEntity):
    """Representation of a Torch Pellet System sensor."""

    entity_description: TorchPelletSystemSensorEntityDescription

    def __init__(
        self,
        coordinator: TorchPelletSystemDataUpdateCoordinator,
        description: TorchPelletSystemSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""

        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{description.key}"

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""

        return self.entity_description.value(self.coordinator.data[Platform.SENSOR])
