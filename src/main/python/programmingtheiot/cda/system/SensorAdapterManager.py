import logging

from importlib import import_module

from apscheduler.schedulers.background import BackgroundScheduler

import programmingtheiot.common.ConfigConst as ConfigConst

from programmingtheiot.common.ConfigUtil import ConfigUtil
from programmingtheiot.common.IDataMessageListener import IDataMessageListener

from programmingtheiot.cda.sim.SensorDataGenerator import SensorDataGenerator
from programmingtheiot.cda.sim.HumiditySensorSimTask import HumiditySensorSimTask
from programmingtheiot.cda.sim.TemperatureSensorSimTask import TemperatureSensorSimTask
from programmingtheiot.cda.sim.PressureSensorSimTask import PressureSensorSimTask

class SensorAdapterManager(object):
    """
    Shell representation of class for student implementation.
    """

    def __init__(self):
        self.configUtil = ConfigUtil()

        # Retrieve configuration values
        self.pollRate = self.configUtil.getInteger(
            section=ConfigConst.CONSTRAINED_DEVICE,
            key=ConfigConst.POLL_CYCLES_KEY,
            defaultVal=ConfigConst.DEFAULT_POLL_CYCLES
        )

        self.useEmulator = self.configUtil.getBoolean(
            section=ConfigConst.CONSTRAINED_DEVICE,
            key=ConfigConst.ENABLE_EMULATOR_KEY
        )

        self.locationID = self.configUtil.getProperty(
            section=ConfigConst.CONSTRAINED_DEVICE,
            key=ConfigConst.DEVICE_LOCATION_ID_KEY,
            defaultVal=ConfigConst.NOT_SET
        )

        if self.pollRate <= 0:
            self.pollRate = ConfigConst.DEFAULT_POLL_CYCLES

        # Scheduler setup
        self.scheduler = BackgroundScheduler()
        self.scheduler.add_job(
            self.handleTelemetry, 
            'interval', 
            seconds=self.pollRate, 
            max_instances=2, 
            coalesce=True, 
            misfire_grace_time=15
        )

        # Initial values for sensors
        self.dataMsgListener = None
        self.humidityAdapter = None
        self.pressureAdapter = None
        self.tempAdapter = None

        # Initialize environmental sensor tasks
        self._initEnvironmentalSensorTasks()

        # Log the emulator or simulator status
        if self.useEmulator:
            logging.info("Using emulators.")
        else:
            logging.info("Using simulators.")

    def _initEnvironmentalSensorTasks(self):
        humidityFloor = self.configUtil.getFloat(
            section=ConfigConst.CONSTRAINED_DEVICE,
            key=ConfigConst.HUMIDITY_SIM_FLOOR_KEY,
            defaultVal=SensorDataGenerator.LOW_NORMAL_ENV_HUMIDITY
        )
        humidityCeiling = self.configUtil.getFloat(
            section=ConfigConst.CONSTRAINED_DEVICE,
            key=ConfigConst.HUMIDITY_SIM_CEILING_KEY,
            defaultVal=SensorDataGenerator.HI_NORMAL_ENV_HUMIDITY
        )

        pressureFloor = self.configUtil.getFloat(
            section=ConfigConst.CONSTRAINED_DEVICE,
            key=ConfigConst.PRESSURE_SIM_FLOOR_KEY,
            defaultVal=SensorDataGenerator.LOW_NORMAL_ENV_PRESSURE
        )
        pressureCeiling = self.configUtil.getFloat(
            section=ConfigConst.CONSTRAINED_DEVICE,
            key=ConfigConst.PRESSURE_SIM_CEILING_KEY,
            defaultVal=SensorDataGenerator.HI_NORMAL_ENV_PRESSURE
        )

        tempFloor = self.configUtil.getFloat(
            section=ConfigConst.CONSTRAINED_DEVICE,
            key=ConfigConst.TEMP_SIM_FLOOR_KEY,
            defaultVal=SensorDataGenerator.LOW_NORMAL_INDOOR_TEMP
        )
        tempCeiling = self.configUtil.getFloat(
            section=ConfigConst.CONSTRAINED_DEVICE,
            key=ConfigConst.TEMP_SIM_CEILING_KEY,
            defaultVal=SensorDataGenerator.HI_NORMAL_INDOOR_TEMP
        )

        if not self.useEmulator:
            self.dataGenerator = SensorDataGenerator()

            # Generate datasets
            humidityData = self.dataGenerator.generateDailyEnvironmentHumidityDataSet(
                minValue=humidityFloor, maxValue=humidityCeiling, useSeconds=False
            )
            pressureData = self.dataGenerator.generateDailyEnvironmentPressureDataSet(
                minValue=pressureFloor, maxValue=pressureCeiling, useSeconds=False
            )
            tempData = self.dataGenerator.generateDailyIndoorTemperatureDataSet(
                minValue=tempFloor, maxValue=tempCeiling, useSeconds=False
            )

            # Create sensor simulation tasks
            self.humidityAdapter = HumiditySensorSimTask(dataSet=humidityData)
            self.pressureAdapter = PressureSensorSimTask(dataSet=pressureData)
            self.tempAdapter = TemperatureSensorSimTask(dataSet=tempData)

    def handleTelemetry(self):
        # Generate telemetry data for each sensor
        humidityData = self.humidityAdapter.generateTelemetry()
        pressureData = self.pressureAdapter.generateTelemetry()
        tempData = self.tempAdapter.generateTelemetry()

        # Set location ID on the sensor data
        humidityData.setLocationID(self.locationID)
        pressureData.setLocationID(self.locationID)
        tempData.setLocationID(self.locationID)

        # Log the generated data
        logging.debug('Generated humidity data: ' + str(humidityData))
        logging.debug('Generated pressure data: ' + str(pressureData))
        logging.debug('Generated temp data: ' + str(tempData))

        # Pass the generated data to the listener
        if self.dataMsgListener:
            self.dataMsgListener.handleSensorMessage(humidityData)
            self.dataMsgListener.handleSensorMessage(pressureData)
            self.dataMsgListener.handleSensorMessage(tempData)

    def setDataMessageListener(self, listener: IDataMessageListener):
        if listener:
            self.dataMsgListener = listener

    def startManager(self) -> bool:
        logging.info("Started SensorAdapterManager.")

        if not self.scheduler.running:
            self.scheduler.start()
            return True
        else:
            logging.info("SensorAdapterManager scheduler already started. Ignoring.")
            return False

    def stopManager(self) -> bool:
        logging.info("Stopped SensorAdapterManager.")

        try:
            self.scheduler.shutdown()
            return True
        except:
            logging.info("SensorAdapterManager scheduler already stopped. Ignoring.")
            return False
