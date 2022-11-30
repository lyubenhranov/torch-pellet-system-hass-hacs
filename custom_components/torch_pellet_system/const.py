"""Constants for the Torch Pellet System integration."""

import logging

DOMAIN = "torch_pellet_system"
LOGGER = logging.getLogger(__package__)

PELLET_SYSTEM_STATE_KEY = "bd_state"
WATER_TEMPERATURE_SETTING_KEY = "bd_s_temp"
WATER_TEMPERATURE_OUT_OF_THE_PELLET_SYSTEM_KEY = "bd_t_curr"
WATER_TEMPERATURE_COMING_IN_THE_PELLET_SYSTEM_KEY = "bd_t_back"
PELLET_BURNER_TEMPERATURE_KEY = "bd_t_body"
LIGTH_SENSOR_KEY = "bd_lux"
BURNER_CURRENT_WORKING_POWER_KEY = "bd_power"
PELLET_SYSTEM_TNC_STATUS_KEY = "link_status"
