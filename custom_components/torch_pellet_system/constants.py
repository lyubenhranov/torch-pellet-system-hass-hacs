"""Constants for the Torch Pellet System integration."""

import logging

DOMAIN = "torch_pellet_system"
LOGGER = logging.getLogger(__package__)

PELLET_SYSTEM_STATE_KEY = "state"
WATER_TEMPERATURE_OUT_OF_THE_PELLET_SYSTEM_KEY = "tOut"
WATER_TEMPERATURE_COMING_IN_THE_PELLET_SYSTEM_KEY = "tIn"
PELLET_BURNER_TEMPERATURE_KEY = "tBody"
LIGTH_SENSOR_KEY = "lux"
BURNER_CURRENT_WORKING_POWER_KEY = "power"
PELLET_SYSTEM_TNC_STATUS_KEY = "status"
BURNED_PELLETS_QUANTITY = "pellets"
