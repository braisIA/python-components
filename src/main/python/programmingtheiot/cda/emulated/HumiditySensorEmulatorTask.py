from programmingtheiot.data.SensorData import SensorData
import programmingtheiot.common.ConfigConst as ConfigConst
from programmingtheiot.common.ConfigUtil import ConfigUtil
from programmingtheiot.cda.sim.BaseSensorSimTask import BaseSensorSimTask
from pisense import SenseHAT

class HumiditySensorEmulatorTask(BaseSensorSimTask):
    """
    Emulated Humidity Sensor Task class.
    """

    def __init__(self, dataSet = None):
        super(HumiditySensorEmulatorTask, self).__init__(
            name=ConfigConst.HUMIDITY_SENSOR_NAME,
            typeID=ConfigConst.HUMIDITY_SENSOR_TYPE
        )

        # Load the configuration to enable the emulator
        enableEmulation = ConfigUtil().getBoolean(
            ConfigConst.CONSTRAINED_DEVICE, ConfigConst.ENABLE_EMULATOR_KEY
        )
        self.sh = SenseHAT(emulate=enableEmulation)

    def generateTelemetry(self) -> SensorData:
        """
        Generate telemetry data by reading the humidity from the emulated sensor.
        """
        sensorData = SensorData(name=self.getName(), typeID=self.getTypeID())
        sensorVal = self.sh.environ.humidity

        sensorData.setValue(sensorVal)
        self.latestSensorData = sensorData

        return sensorData
