"""
sensor_data_ingest_mqtt_dev

"""
import argparse
import json
import random
import sys
import threading
import time
from uuid import uuid4

from awscrt import auth, http, io, mqtt
from awsiot import mqtt_connection_builder

from .topic_config import read_config

# setup:
received_count = 0
received_all_event = threading.Event()
args = 0


def mqtt_pub():
    """
    Publish a random stream of messages to the AWS IoT Core MQTT broker
    """
    global args
    args = parse_args()
    init(args)
    mqtt_connection = setup_connection(args)

    connect_future = mqtt_connection.connect()
    # Future.result() waits until a result is available
    connect_future.result()
    print("Connected!")

    topic_data = read_config()
    print(f"platform_type: {topic_data['platform_type']}")
    print(f"random platform_type: {random.choice(topic_data['platform_type'])}")

    # Publish message to server desired number of times
    # This step loops forever if count was set to 0
    if args.count == 0:
        print("Sending messages until program killed")
    else:
        print(f"Sending {args.count} message(s)")

    publish_count = 1
    while (publish_count <= args.count) or (args.count == 0):

        # topic definition: generate a random topic to publish to, based on the established hierarchy:
        # ex: IOOS/<platform_type>/<ra>/<platform>/<sensor>/<variable>
        platform_type = random.choice(topic_data["platform_type"])
        ra = random.choice(topic_data["ra"])
        platform = random.choice(topic_data["platform"])
        sensor = random.choice(topic_data["sensor"])
        variable = random.choice(topic_data["variable"])

        topic = f"IOOS/{platform_type}/{ra}/{platform}/{sensor}/{variable}"
        obs_data = random.uniform(1, 100)
        msg_json = """
            { "metadata": {
                "platform_type": "{platform_type}",
                "ra": "{ra}",
                "platform": "{platform}",
                "sensor": "{sensor}",
                "variable": "{variable}"
                },
            "data": {
                "value": "{data}"
                }
            }
        """
        msg_dict = dict()
        msg_dict["metadata"] = {
            "platform_type": platform_type,
            "ra": ra,
            "platform": platform,
            "sensor": sensor,
            "variable": variable,
        }
        msg_dict["data"] = {"value": obs_data}
        # print(msg_dict)

        print(f"Topic: {topic}")
        print(f"Message: {msg_dict}")
        mqtt_connection.publish(
            topic=topic,
            # payload=str(msg_dict),
            payload=json.dumps(msg_dict),
            qos=mqtt.QoS.AT_LEAST_ONCE,
        )
        time.sleep(1)
        publish_count += 1

    # Disconnect
    print("Disconnecting...")
    disconnect_future = mqtt_connection.disconnect()
    disconnect_future.result()
    print("Disconnected!")


def mqtt_sub():
    """
    Subscribe and echo messages from the broker using a user-provided topic filter string
    """
    global args
    args = parse_args()
    init(args)
    mqtt_connection = setup_connection(args)

    connect_future = mqtt_connection.connect()
    # Future.result() waits until a result is available
    connect_future.result()
    print("Connected!")

    # Subscribe
    print(f"Subscribing to topic '{args.subscribe_topic}'...")
    subscribe_future, packet_id = mqtt_connection.subscribe(
        topic=args.subscribe_topic,
        qos=mqtt.QoS.AT_LEAST_ONCE,
        callback=on_message_received,
    )

    subscribe_result = subscribe_future.result()
    print("Subscribed with {}".format(str(subscribe_result["qos"])))

    # Wait for all messages to be received.
    # This waits forever if count was set to 0.
    if args.count != 0 and not received_all_event.is_set():
        print("Waiting for all messages to be received...")

    received_all_event.wait()
    print(f"{received_count} message(s) received.")

    # Disconnect
    print("Disconnecting...")
    disconnect_future = mqtt_connection.disconnect()
    disconnect_future.result()
    print("Disconnected!")


def init(args):
    """
    Main setup function
    """
    io.init_logging(getattr(io.LogLevel, args.verbosity), "stderr")

    # global received_count = 0
    # global received_all_event = threading.Event()


def setup_connection(args):
    """
    Set up an MQTT client connection and other details
    """

    event_loop_group = io.EventLoopGroup(1)
    host_resolver = io.DefaultHostResolver(event_loop_group)
    client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)

    if args.use_websocket == True:
        proxy_options = None
        if args.proxy_host:
            proxy_options = http.HttpProxyOptions(
                host_name=args.proxy_host,
                port=args.proxy_port,
            )

        credentials_provider = auth.AwsCredentialsProvider.new_default_chain(
            client_bootstrap,
        )
        mqtt_connection = mqtt_connection_builder.websockets_with_default_aws_signing(
            endpoint=args.endpoint,
            client_bootstrap=client_bootstrap,
            region=args.signing_region,
            credentials_provider=credentials_provider,
            websocket_proxy_options=proxy_options,
            ca_filepath=args.root_ca,
            on_connection_interrupted=on_connection_interrupted,
            on_connection_resumed=on_connection_resumed,
            client_id=args.client_id,
            clean_session=False,
            keep_alive_secs=6,
        )

    else:
        mqtt_connection = mqtt_connection_builder.mtls_from_path(
            endpoint=args.endpoint,
            cert_filepath=args.cert,
            pri_key_filepath=args.key,
            client_bootstrap=client_bootstrap,
            ca_filepath=args.root_ca,
            on_connection_interrupted=on_connection_interrupted,
            on_connection_resumed=on_connection_resumed,
            client_id=args.client_id,
            clean_session=False,
            keep_alive_secs=6,
        )

    print(
        f"Connecting to {args.endpoint} with client ID '{args.client_id}'...",
    )

    return mqtt_connection


# Callback when the subscribed topic receives a message
def on_message_received(topic, payload, **kwargs):
    print(f"Received message from topic '{topic}': {payload}")
    global received_count
    received_count += 1
    if received_count == args.count:
        received_all_event.set()


# Callback when connection is accidentally lost.
def on_connection_interrupted(connection, error, **kwargs):
    print(f"Connection interrupted. error: {error}")


# Callback when an interrupted connection is re-established.
def on_connection_resumed(connection, return_code, session_present, **kwargs):
    print(
        "Connection resumed. return_code: {} session_present: {}".format(
            return_code,
            session_present,
        ),
    )

    if return_code == mqtt.ConnectReturnCode.ACCEPTED and not session_present:
        print("Session did not persist. Resubscribing to existing topics...")
        resubscribe_future, _ = connection.resubscribe_existing_topics()

        # Cannot synchronously wait for resubscribe result because we're on the connection's event-loop thread,
        # evaluate result with a callback instead.
        resubscribe_future.add_done_callback(on_resubscribe_complete)


def on_resubscribe_complete(resubscribe_future):
    resubscribe_results = resubscribe_future.result()
    print(f"Resubscribe results: {resubscribe_results}")

    for topic, qos in resubscribe_results["topics"]:
        if qos is None:
            sys.exit(f"Server rejected resubscribe to topic: {topic}")


def parse_args():
    """
    Parse command-line args passed in to either entrypoint function
    """

    kwargs = {
        "description": "A simple utility that leverages the AWS IoT SDK publish and subscribe to MQTT topics",
        "formatter_class": argparse.RawDescriptionHelpFormatter,
    }
    parser = argparse.ArgumentParser(**kwargs)

    parser.add_argument(
        "--endpoint",
        required=True,
        help="Your AWS IoT custom endpoint, not including a port. "
        + 'Ex: "abcd123456wxyz-ats.iot.us-east-1.amazonaws.com"',
    )
    parser.add_argument(
        "--cert",
        help="File path to your client certificate, in PEM format.",
    )
    parser.add_argument("--key", help="File path to your private key, in PEM format.")
    parser.add_argument(
        "--root-ca",
        help="File path to root certificate authority, in PEM format. "
        + "Necessary if MQTT server uses a certificate that's not already in "
        + "your trust store.",
    )
    parser.add_argument(
        "--client-id",
        default="test-" + str(uuid4()),
        help="Client ID for MQTT connection.",
    )
    parser.add_argument(
        "--subscribe_topic",
        default="IOOS/#",
        help="Topic to subscribe to.",
    )
    # parser.add_argument('--message', default="Hello World!", help="Message to publish. " +
    #                                                              "Specify empty string to publish nothing.")
    parser.add_argument(
        "--count",
        default=0,
        type=int,
        help="Number of messages to publish/receive before exiting. "
        + "Specify 0 to run forever.",
    )
    parser.add_argument(
        "--use-websocket",
        default=False,
        action="store_true",
        help="To use a websocket instead of raw mqtt. If you "
        + "specify this option you must specify a region for signing, you can also enable proxy mode.",
    )
    parser.add_argument(
        "--signing-region",
        default="us-east-1",
        help="If you specify --use-web-socket, this "
        + "is the region that will be used for computing the Sigv4 signature",
    )
    # parser.add_argument('--proxy-host', help="Hostname for proxy to connect to. Note: if you use this feature, " +
    #    "you will likely need to set --root-ca to the ca for your proxy.")
    # parser.add_argument('--proxy-port', type=int, default=8080, help="Port for proxy to connect to.")
    parser.add_argument(
        "--verbosity",
        choices=[x.name for x in io.LogLevel],
        default=io.LogLevel.NoLogs.name,
        help="Logging level",
    )

    args = parser.parse_args()
    return args
