#####
# 
# This class is part of the Programming the Internet of Things project.
# 
# It is provided as a simple shell to guide the student and assist with
# implementation for the Programming the Internet of Things exercises,
# and designed to be modified by the student as needed.
#

import logging

from programmingtheiot.cda.sim.BaseSensorSimTask import BaseSensorSimTask
from programmingtheiot.cda.sim.SensorDataGenerator import SensorDataGenerator
import programmingtheiot.common.ConfigConst as ConfigConst

class HumiditySensorSimTask(BaseSensorSimTask):
    """
    Implementación de la tarea de simulación del sensor de humedad.
    """

    def __init__(self, dataSet=None):
        super(HumiditySensorSimTask, self).__init__(
            name=ConfigConst.HUMIDITY_SENSOR_NAME,
            typeID=ConfigConst.HUMIDITY_SENSOR_TYPE,
            dataSet=dataSet,
            minVal=SensorDataGenerator.LOW_NORMAL_ENV_HUMIDITY,
            maxVal=SensorDataGenerator.HI_NORMAL_ENV_HUMIDITY
        )
