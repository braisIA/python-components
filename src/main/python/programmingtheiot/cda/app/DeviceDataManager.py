import logging

from programmingtheiot.cda.connection.CoapClientConnector import CoapClientConnector
from programmingtheiot.cda.connection.MqttClientConnector import MqttClientConnector

from programmingtheiot.cda.system.ActuatorAdapterManager import ActuatorAdapterManager
from programmingtheiot.cda.system.SensorAdapterManager import SensorAdapterManager
from programmingtheiot.cda.system.SystemPerformanceManager import SystemPerformanceManager

from programmingtheiot.common.IDataMessageListener import IDataMessageListener
from programmingtheiot.common.ISystemPerformanceDataListener import ISystemPerformanceDataListener
from programmingtheiot.common.ITelemetryDataListener import ITelemetryDataListener
from programmingtheiot.common.ResourceNameEnum import ResourceNameEnum
import programmingtheiot.common.ConfigConst as ConfigConst
from programmingtheiot.common.ConfigUtil import ConfigUtil

from programmingtheiot.data.ActuatorData import ActuatorData
from programmingtheiot.data.SensorData import SensorData
from programmingtheiot.data.SystemPerformanceData import SystemPerformanceData


class DeviceDataManager(IDataMessageListener):
    """
    Implementation of the DeviceDataManager class for managing device data.
    """

    def __init__(self):
        logging.info("Initializing DeviceDataManager...")

        self.sysPerfMgr = SystemPerformanceManager()
        self.sensorAdapterMgr = SensorAdapterManager()
        self.actuatorAdapterMgr = ActuatorAdapterManager(dataMsgListener=self)

        # Crear instancia de ConfigUtil para leer la configuración
        self.configUtil = ConfigUtil()

        # Inicializar MQTT si está habilitado
        self.enableMqttClient = self.configUtil.getBoolean(
            section=ConfigConst.CONSTRAINED_DEVICE, 
            key=ConfigConst.ENABLE_MQTT_CLIENT_KEY
        )

        self.mqttClient = None
        if self.enableMqttClient:
            self.mqttClient = MqttClientConnector()
            self.mqttClient.setDataMessageListener(self)

        # Inicializar CoAP si está habilitado
        self.enableCoapClient = self.configUtil.getBoolean(
            section=ConfigConst.CONSTRAINED_DEVICE,
            key=ConfigConst.ENABLE_COAP_CLIENT_KEY
        )

        self.coapClient = None
        if self.enableCoapClient:
            self.coapClient = CoapClientConnector(dataMsgListener=self)

        self.sysPerfMgr.setDataMessageListener(self)
        self.sensorAdapterMgr.setDataMessageListener(self)

        self.actuatorResponseCache = {}

        logging.info("DeviceDataManager initialization complete.")

    def getLatestActuatorDataResponseFromCache(self, name: str = None) -> ActuatorData:
        logging.debug(f"Retrieving latest actuator data response for {name}.")
        return self.actuatorResponseCache.get(name)

    def getLatestSensorDataFromCache(self, name: str = None) -> SensorData:
        logging.debug(f"Retrieving latest sensor data for {name}.")
        return None

    def getLatestSystemPerformanceDataFromCache(self, name: str = None) -> SystemPerformanceData:
        logging.debug(f"Retrieving latest system performance data for {name}.")
        return None

    def handleActuatorCommandMessage(self, data: ActuatorData) -> bool:
        if data:
            logging.info(f"Processing actuator command: {data}")
            return self.actuatorAdapterMgr.sendActuatorCommand(data)
        logging.warning("Received null actuator command message. Ignoring.")
        return False

    def handleActuatorCommandResponse(self, data: ActuatorData) -> bool:
        if data:
            logging.debug(f"Processing actuator command response: {data}")
            self.actuatorResponseCache[data.getName()] = data
            self._handleUpstreamTransmission(ResourceNameEnum.CDA_ACTUATOR_RESPONSE_RESOURCE, str(data))
            return True
        logging.warning("Received null actuator command response. Ignoring.")
        return False

    def handleIncomingMessage(self, resourceEnum: ResourceNameEnum, msg: str) -> bool:
        logging.debug(f"Handling incoming message for resource {resourceEnum}: {msg}")
        return True

    def handleSensorMessage(self, data: SensorData) -> bool:
        if data:
            logging.info(f"Processing sensor message: {data}")
            self._handleSensorDataAnalysis(data)
            return True
        logging.warning("Received null sensor message. Ignoring.")
        return False

    def handleSystemPerformanceMessage(self, data: SystemPerformanceData) -> bool:
        if data:
            logging.info(f"Processing system performance message: {data}")
            self._handleUpstreamTransmission(ResourceNameEnum.CDA_SYSTEM_PERF_MSG_RESOURCE, str(data))
            return True
        logging.warning("Received null system performance message. Ignoring.")
        return False

    def setSystemPerformanceDataListener(self, listener: ISystemPerformanceDataListener = None):
        logging.debug("Setting system performance data listener.")

    def setTelemetryDataListener(self, name: str = None, listener: ITelemetryDataListener = None):
        logging.debug(f"Setting telemetry data listener for {name}.")

    def startManager(self):
        logging.info("Starting DeviceDataManager...")
        self.sysPerfMgr.startManager()
        self.sensorAdapterMgr.startManager()

        if self.mqttClient:
            self.mqttClient.connectClient()
            self.mqttClient.subscribeToTopic(
                ResourceNameEnum.CDA_ACTUATOR_CMD_RESOURCE,
                callback=None,
                qos=ConfigConst.DEFAULT_QOS
            )

        logging.info("DeviceDataManager started.")

    def stopManager(self):
        logging.info("Stopping DeviceDataManager...")
        self.sysPerfMgr.stopManager()
        self.sensorAdapterMgr.stopManager()

        if self.mqttClient:
            self.mqttClient.unsubscribeFromTopic(ResourceNameEnum.CDA_ACTUATOR_CMD_RESOURCE)
            self.mqttClient.disconnectClient()

        logging.info("DeviceDataManager stopped.")

    def _handleIncomingDataAnalysis(self, msg: str):
        logging.debug(f"Analyzing incoming data: {msg}")

    def _handleSensorDataAnalysis(self, data: SensorData):
        logging.debug(f"Analyzing sensor data: {data}")

    def _handleUpstreamTransmission(self, resourceName: ResourceNameEnum, msg: str):
        logging.debug(f"Transmitting data upstream for resource {resourceName}: {msg}")
