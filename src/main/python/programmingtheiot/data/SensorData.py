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
    Represents sensor data with support for floating-point values.
    Inherits from BaseIotData.
    """
    
    def __init__(self, typeID: int = ConfigConst.DEFAULT_SENSOR_TYPE, name = ConfigConst.NOT_SET, d = None):
        super(SensorData, self).__init__(name = name, typeID = typeID, d = d)
        self.value = ConfigConst.DEFAULT_VAL
    
    def getValue(self) -> float:
        """Returns the current sensor value."""
        return self.value
    
    def setValue(self, newVal: float):
        """Sets the sensor value and updates the timestamp."""
        self.value = newVal
        self.updateTimeStamp()
    
    def _handleUpdateData(self, data):
        """Handles updating data from another SensorData instance."""
        if isinstance(data, SensorData):
            self.value = data.getValue()
        else:
            raise TypeError("Expected instance of SensorData")
    
    def __str__(self):
        return f"SensorData(name={self.name}, typeID={self.typeID}, value={self.value}, timestamp={self.timeStamp})"
