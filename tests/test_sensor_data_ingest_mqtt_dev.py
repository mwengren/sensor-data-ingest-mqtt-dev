import numpy as np
import pytest

#from sensor_data_ingest_mqtt_dev import meaning_of_life, meaning_of_life_url
import sensor_data_ingest_mqtt_dev.mqtt_dev


@pytest.mark.web
def test_mqtt_pub():
    ret = mqtt_pub()

    assert isinstance(ret, dict)
    assert "platform_type" in ret
    assert "ra" in ret
    assert "platform" in ret


def test_mqtt_sub():
    ret = mqtt_pub()
    assert isinstance(ret, str)
