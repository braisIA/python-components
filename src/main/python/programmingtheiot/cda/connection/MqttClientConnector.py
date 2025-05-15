#####
#
# This class is part of the Programming the Internet of Things project.
#
# It is provided as a simple shell to guide the student and assist with
# implementation for the Programming the Internet of Things exercises,
# and designed to be modified by the student as needed.
#

import logging
import paho.mqtt.client as mqttClient

import programmingtheiot.common.ConfigConst as ConfigConst

from programmingtheiot.common.ConfigUtil import ConfigUtil
from programmingtheiot.common.IDataMessageListener import IDataMessageListener
from programmingtheiot.common.ResourceNameEnum import ResourceNameEnum

from programmingtheiot.cda.connection.IPubSubClient import IPubSubClient

class MqttClientConnector(IPubSubClient):
	"""
	Implementation of an MQTT client connector using the paho-mqtt package.
	"""

	def __init__(self, clientID: str = None):
		self.config = ConfigUtil()
		self.dataMsgListener = None

		self.host = self.config.getProperty(
			ConfigConst.MQTT_GATEWAY_SERVICE, ConfigConst.HOST_KEY, ConfigConst.DEFAULT_HOST)

		self.port = self.config.getInteger(
			ConfigConst.MQTT_GATEWAY_SERVICE, ConfigConst.PORT_KEY, ConfigConst.DEFAULT_MQTT_PORT)

		self.keepAlive = self.config.getInteger(
			ConfigConst.MQTT_GATEWAY_SERVICE, ConfigConst.KEEP_ALIVE_KEY, ConfigConst.DEFAULT_KEEP_ALIVE)

		self.defaultQos = self.config.getInteger(
			ConfigConst.MQTT_GATEWAY_SERVICE, ConfigConst.DEFAULT_QOS_KEY, ConfigConst.DEFAULT_QOS)

		self.mqttClient = None

		if not clientID:
			self.clientID = self.config.getProperty(
				ConfigConst.CONSTRAINED_DEVICE, ConfigConst.DEVICE_LOCATION_ID_KEY)
		else:
			self.clientID = clientID

		logging.info('\tMQTT Client ID:   ' + self.clientID)
		logging.info('\tMQTT Broker Host: ' + self.host)
		logging.info('\tMQTT Broker Port: ' + str(self.port))
		logging.info('\tMQTT Keep Alive:  ' + str(self.keepAlive))

	def connectClient(self) -> bool:
		if not self.mqttClient:
			self.mqttClient = mqttClient.Client(client_id=self.clientID, clean_session=True)

			self.mqttClient.on_connect = self.onConnect
			self.mqttClient.on_disconnect = self.onDisconnect
			self.mqttClient.on_message = self.onMessage
			self.mqttClient.on_publish = self.onPublish
			self.mqttClient.on_subscribe = self.onSubscribe

		if not self.mqttClient.is_connected():
			logging.info('MQTT client connecting to broker at host: ' + self.host)
			self.mqttClient.connect(self.host, self.port, self.keepAlive)
			self.mqttClient.loop_start()
			return True
		else:
			logging.warning('MQTT client is already connected. Ignoring connect request.')
			return False

	def disconnectClient(self) -> bool:
		if self.mqttClient and self.mqttClient.is_connected():
			logging.info('Disconnecting MQTT client from broker: ' + self.host)
			self.mqttClient.loop_stop()
			self.mqttClient.disconnect()
			return True
		else:
			logging.warning('MQTT client already disconnected. Ignoring.')
			return False

	def setDataMessageListener(self, listener: IDataMessageListener = None) -> bool:
		self.dataMsgListener = listener
		logging.info('Data message listener has been set.')
		return True

	def onConnect(self, client, userdata, flags, rc):
		logging.info(f'Connected to MQTT broker. Result code: {rc}')

	def onDisconnect(self, client, userdata, rc):
		logging.info(f'Disconnected from MQTT broker. Result code: {rc}')

	def onMessage(self, client, userdata, msg):
		payload = msg.payload.decode("utf-8") if msg.payload else None
		if payload:
			logging.info(f'Message received on topic {msg.topic}: {payload}')
			if self.dataMsgListener:
				self.dataMsgListener.handleMessage(msg.topic, payload)
		else:
			logging.info(f'Message received on topic {msg.topic} with no payload.')

	def onPublish(self, client, userdata, mid):
		logging.info(f'Message published. mid: {mid}')

	def onSubscribe(self, client, userdata, mid, granted_qos):
		logging.info(f'Subscribed. mid: {mid}, QoS: {granted_qos}')

	def onActuatorCommandMessage(self, client, userdata, msg):
		logging.info(f'Actuator command received on topic {msg.topic}: {msg.payload.decode("utf-8")}')

	def publishMessage(self, resource: ResourceNameEnum = None, msg: str = None, qos: int = ConfigConst.DEFAULT_QOS) -> bool:
		if not resource:
			logging.warning('No topic specified. Cannot publish message.')
			return False

		if not msg:
			logging.warning('No message specified. Cannot publish message to topic: ' + resource.value)
			return False

		if qos < 0 or qos > 2:
			qos = ConfigConst.DEFAULT_QOS

		msgInfo = self.mqttClient.publish(topic=resource.value, payload=msg, qos=qos)
		msgInfo.wait_for_publish()
		logging.info(f'Published message to topic [{resource.value}]: {msg}')
		return True

	def subscribeToTopic(self, resource: ResourceNameEnum = None, callback=None, qos: int = ConfigConst.DEFAULT_QOS) -> bool:
		if not resource:
			logging.warning('No topic specified. Cannot subscribe.')
			return False

		if qos < 0 or qos > 2:
			qos = ConfigConst.DEFAULT_QOS

		topic = resource.value
		if callback:
			self.mqttClient.message_callback_add(topic, callback)

		logging.info(f'Subscribing to topic {topic}')
		self.mqttClient.subscribe(topic, qos)

		return True

	def unsubscribeFromTopic(self, resource: ResourceNameEnum = None) -> bool:
		if not resource:
			logging.warning('No topic specified. Cannot unsubscribe.')
			return False

		topic = resource.value
		logging.info(f'Unsubscribing from topic {topic}')
		self.mqttClient.unsubscribe(topic)

		return True

	def setDataMessageListener(self, listener: IDataMessageListener = None) -> bool:
		pass
