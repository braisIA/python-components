#####
# 
# This class is part of the Programming the Internet of Things project.
# 
# It is provided as a simple shell to guide the student and assist with
# implementation for the Programming the Internet of Things exercises,
# and designed to be modified by the student as needed.
#

import programmingtheiot.common.ConfigConst as ConfigConst

from programmingtheiot.data.BaseIotData import BaseIotData

class SensorData(BaseIotData):
    """
    Representa los datos de un sensor, heredando de BaseIotData.
    Proporciona un valor flotante como lectura del sensor.
    """

    def __init__(self, typeID: int = ConfigConst.DEFAULT_SENSOR_TYPE, name = ConfigConst.NOT_SET, d = None):
        super(SensorData, self).__init__(name=name, typeID=typeID, d=d)
        self.value = ConfigConst.DEFAULT_VAL

    def getValue(self) -> float:
        """
        Devuelve el valor actual del sensor.
        """
        return self.value

    def setValue(self, newVal: float):
        """
        Establece un nuevo valor para el sensor y actualiza el timestamp.
        """
        self.value = newVal
        self.updateTimeStamp()

    def _handleUpdateData(self, data):
        """
        Actualiza los datos del sensor desde otra instancia de SensorData.
        """
        if isinstance(data, SensorData):
            self.value = data.getValue()
        else:
            raise TypeError("Se esperaba una instancia de SensorData")

    def __str__(self):
        return (
            f"SensorData [ name = {self.name}, typeID = {self.typeID}, "
            f"value = {self.value}, timestamp = {self.timeStamp} ]"
        )
