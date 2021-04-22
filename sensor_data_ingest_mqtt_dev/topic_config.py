"""
topic_config

"""


def read_config():
    """
    read JSON config file for topic options
    """
    topic_data = {
        "platform_type": ["buoy", "station", "glider"],
        "ra": [
            "aoos",
            "caricoos",
            "cencoos",
            "gcoos",
            "glos",
            "maracoos",
            "nanoos",
            "neracoos",
            "pacioos",
            "secoora",
            "sccoos",
        ],
        "platform": ["a", "b", "c", "d", "e", "f", "g", "h"],
        "sensor": ["met", "ctd", "adcp", "wave", "bio"],
        "variable": [
            "air_temperature",
            "air_pressure_at_sea_level",
            "sea_water_practical_salinity",
            "sea_water_temperature",
            "sea_surface_wave_significant_height",
            "mass_concentration_of_chlorophyll_in_sea_water",
            "eastward_sea_water_velocity",
            "northward_sea_water_velocity",
            "mass_concentration_of_chlorophyll_in_sea_water",
        ],
    }
    # json.dumps(topic_data, sort_keys=True, indent=4)
    return topic_data
