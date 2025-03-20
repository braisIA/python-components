import logging
import random

import programmingtheiot.common.ConfigConst as ConfigConst
from programmingtheiot.data.SensorData import SensorData
from programmingtheiot.cda.sim.SensorDataGenerator import SensorDataSet

class BaseSensorSimTask:
    """
    Base class for simulating sensor data.
    """

    DEFAULT_MIN_VAL = ConfigConst.DEFAULT_VAL
    DEFAULT_MAX_VAL = 100.0

    def __init__(self, name: str = ConfigConst.NOT_SET, typeID: int = ConfigConst.DEFAULT_SENSOR_TYPE, dataSet: SensorDataSet = None, minVal: float = DEFAULT_MIN_VAL, maxVal: float = DEFAULT_MAX_VAL):
        """
        Initializes the BaseSensorSimTask with a name, typeID, and optional dataset.
        If no dataset is provided, it uses a randomizer.
        """
        self.dataSet = dataSet
        self.name = name
        self.typeID = typeID
        self.dataSetIndex = 0
        self.useRandomizer = dataSet is None
        self.minVal = minVal
        self.maxVal = maxVal
        self.latestSensorData = None

    def getName(self) -> str:
        """
        Returns the sensor name.
        """
        return self.name

    def getTypeID(self) -> int:
        """
        Returns the sensor type ID.
        """
        return self.typeID

    def generateTelemetry(self) -> SensorData:
        """
        Generates new telemetry data.
        Uses a random value if no dataset is provided.
        """
        sensorData = SensorData(typeID=self.getTypeID(), name=self.getName())
        sensorVal = ConfigConst.DEFAULT_VAL

        if self.useRandomizer:
            sensorVal = random.uniform(self.minVal, self.maxVal)
        else:
            sensorVal = self.dataSet.getDataEntry(index=self.dataSetIndex)
            self.dataSetIndex += 1

            if self.dataSetIndex >= self.dataSet.getDataEntryCount():
                self.dataSetIndex = 0

        sensorData.setValue(sensorVal)
        self.latestSensorData = sensorData

        return self.latestSensorData

    def getTelemetryValue(self) -> float:
        """
        Returns the latest telemetry value.
        If no data exists, generates new telemetry data first.
        """
        if not self.latestSensorData:
            self.generateTelemetry()

        return self.latestSensorData.getValue()

    def getLatestTelemetry(self) -> SensorData:
        """
        Returns the latest SensorData instance.
        """
        return self.latestSensorData
