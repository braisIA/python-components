import logging
import unittest
from time import sleep

from programmingtheiot.cda.connection.MqttClientConnector import MqttClientConnector
from programmingtheiot.common.ResourceNameEnum import ResourceNameEnum
from programmingtheiot.data.ActuatorData import ActuatorData
from programmingtheiot.data.DataUtil import DataUtil

class MqttClientControlPacketTest(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		logging.basicConfig(
			format='%(asctime)s [%(levelname)s] %(message)s',
			level=logging.DEBUG
		)
		logging.info("Iniciando MqttClientControlPacketTest...")

		# Usa un clientID único para evitar colisiones con otros clientes MQTT
		cls.mqttClient = MqttClientConnector(clientID="TestClient-MQTT-Control")
		cls.dataUtil = DataUtil()

	def testConnectAndDisconnect(self):
		logging.info("==> Test: Conexión y desconexión MQTT")

		self.mqttClient.connectClient()
		sleep(2)  # Espera para establecer conexión
		self.mqttClient.disconnectClient()
		sleep(1)  # Espera para ver el paquete DISCONNECT en logs

	def testServerPing(self):
		logging.info("==> Test: PING al servidor MQTT")

		self.mqttClient.connectClient()
		logging.info("Esperando 70 segundos para forzar envío de PINGREQ...")
		sleep(70)  # > 60s (default keep-alive) para forzar PINGREQ
		self.mqttClient.disconnectClient()

	def testPubSubQoS(self):
		logging.info("==> Test: Publicación y suscripción con QoS 1 y 2")

		self.mqttClient.connectClient()
		sleep(2)

		for qos in [1, 2]:
			logging.info(f"Publicando y suscribiendo con QoS {qos}")

			topic = ResourceNameEnum.CDA_ACTUATOR_CMD_RESOURCE

			self.mqttClient.subscribeToTopic(topic, qos=qos)
			sleep(1)

			actuatorData = ActuatorData()
			payload = self.dataUtil.actuatorDataToJson(actuatorData)

			self.mqttClient.publishMessage(topic, payload, qos=qos)
			sleep(1)

			self.mqttClient.unsubscribeFromTopic(topic)
			sleep(1)

		self.mqttClient.disconnectClient()
