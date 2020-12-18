## ioos_pkg_skeleton

[![Build Status](https://travis-ci.com/ioos/ioos-python-package-skeleton.svg?branch=master)](https://travis-ci.com/ioos/ioos-python-package-skeleton)

Quick description

### Documentation and UsagT

URLs for the docs and code.

First, configure an AWS IoT Core Thing with associated security artifacts.  See instructions in [this AWS IoT tutorial](https://docs.aws.amazon.com/iot/latest/developerguide/create-iot-resources.html) for an example.  

The resources created and certificates downloaded are used in the examples below.

### Installation
Not sure these are available currently...

For `conda` users you can

```shell
conda install --channel conda-forge sensor_data_ingest_mqtt_dev
```

or, if you are a `pip` users

```shell
pip install sensor_data_ingest_mqtt_dev
```

### Example

Publish a random stream of MQTT topics according to the Cloud Sensor Data Ingest/IOOS topic hierarchy:
```python
mqtt_pub --root-ca certs/AmazonRootCA1.pem --cert certs/device.pem.crt --key certs/private.pem.key --endpoint <your-iot-endpoint>.us-east-1.amazonaws.com

```
The topics published to are randomized from a pre-configured dictionary of possible MQTT topics.  Refer to topic_config.py.

Subscribe examples:
```python
# topic filter: IOOS/+/neracoos/+/met/#
# (data from any NERACOOS 'met' sensor)
mqtt_sub --root-ca certs/AmazonRootCA1.pem --cert certs/device.pem.crt --key certs/private.pem.key --endpoint <your-iot-endpoint>.us-east-1.amazonaws.com --subscribe_topic IOOS/+/neracoos/+/met/#

# topic filter: IOOS/glider/+/+/ctd/#
# (data from any IOOS glider CTD sensor)
mqtt_sub --root-ca certs/AmazonRootCA1.pem --cert certs/device.pem.crt --key certs/private.pem.key --endpoint <your-iot-endpoint>.us-east-1.amazonaws.com --subscribe_topic IOOS/glider/+/+/ctd/#

```


## Get in touch

Report bugs, suggest features or view the source code on [GitHub](https://github.com/ioos/ioos_pkg_skeleton/issues).


## License and copyright

ioos_pkg_skeleton is licensed under BSD 3-Clause "New" or "Revised" License (BSD-3-Clause).

Development occurs on GitHub at <https://github.com/ioos/ioos_pkg_skeleton>.
