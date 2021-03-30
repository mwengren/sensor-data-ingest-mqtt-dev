import numpy as np
import pytest

import sensor_data_ingest_mqtt_dev.mqtt_dev
from sensor_data_ingest_mqtt_dev.topic_config import read_config

@pytest.fixture
def topic_config():
    return read_config()

def test_read_config(topic_config):
    assert isinstance(topic_config, dict)
    for key in ['platform_type','ra','platform','sensor','variable']:
        assert key in topic_config.keys()
