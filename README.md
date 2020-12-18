## sensor_data_ingest_mqtt_dev

[![Build Status](https://travis-ci.com/ioos/ioos-python-package-skeleton.svg?branch=master)](https://travis-ci.com/ioos/ioos-python-package-skeleton)

A basic AWS IoT MQTT test client that publishes randomized messages according to the proposed IOOS MQTT sensor data topic hierarchy.

**IOOS/\<platform_type\>/\<region\>/\<platform_id\>/<sensor_package/dataset\>/\<standard_name\>**

### Documentation and Usage

First, configure an AWS IoT Core Thing with associated security artifacts.  See instructions in [this AWS IoT tutorial](https://docs.aws.amazon.com/iot/latest/developerguide/create-iot-resources.html) for an example.  

The resources created and certificates downloaded are used in the examples below.

### Installation
Installation in development mode via pip:
```
git clone https://github.com/mwengren/sensor-data-ingest-mqtt-dev.git
cd sensor-data-ingest-mqtt-dev
pip install -e .
```

**Not sure these are available just yet...**

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

**IOOS/\<platform_type\>/\<region\>/\<platform_id\>/<sensor_package/dataset\>/\<standard_name\>**


```python
mqtt_pub --root-ca certs/AmazonRootCA1.pem --cert certs/device.pem.crt --key certs/private.pem.key --endpoint <your-iot-endpoint>.us-east-1.amazonaws.com

```

Example topic: **IOOS/buoy/NERACOOS/E01/met/air_temperature**  

This lets us subscribe many different ways and levels:

* ```IOOS/buoy/NERACOOS/E01/met/air_temperature``` - allows me to get just the most recent values for Air Temperature from E01.
* ```IOOS/buoy/NERACOOS/E01/met/#``` - will get all values from the met dataset.
* ```IOOS/buoy/NERACOOS/E01/#``` - send me any value from E01 as soon as it’s received.
* ```IOOS/buoy/NERACOOS/#``` - see the real time data from any NERACOOS buoy.
* ```IOOS/buoy/#``` - show any buoy data.
* ```IOOS/#``` - show me any new data from any IOOS device that’s ready for public consumption.

The topics published via ```mqtt_pub``` are randomized from a pre-configured dictionary of dummy values following the hierarchy above and published one per second to the IoT Core 'Thing' configured via the AWS console, authenticated with the associated certificates.  Refer to topic_config.py for dummy data used.

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

Report bugs, suggest features or view the source code on [GitHub](https://github.com/mwengren/sensor-data-ingest-mqtt-dev/issues).


## License and copyright

ioos_pkg_skeleton is licensed under BSD 3-Clause "New" or "Revised" License (BSD-3-Clause).

Development occurs on GitHub at <https://github.com/mwengren/sensor-data-ingest-mqtt-dev>.
