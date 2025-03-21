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

class ActuatorData(BaseIotData):
    """
    Represents an actuator command with support for float values and state messages.
    """
    
    def __init__(self, name=ConfigConst.NOT_SET, typeID=ConfigConst.DEFAULT_ACTUATOR_TYPE, d=None):
        super().__init__(name=name, typeID=typeID, d=d)
        self.value = ConfigConst.DEFAULT_VAL
        self.command = ConfigConst.DEFAULT_COMMAND
        self.stateData = ""
    
    def getValue(self) -> float:
        return self.value
    
    def setValue(self, val: float):
        self.value = val
    
    def getCommand(self) -> int:
        return self.command
    
    def setCommand(self, command: int):
        self.command = command
        self.updateTimeStamp()
    
    def getStateData(self) -> str:
        return self.stateData
    
    def setStateData(self, stateData: str):
        self.stateData = stateData
    
    def _handleUpdateData(self, data):
        if isinstance(data, ActuatorData):
            try:
                self.value = data.getValue()
                self.command = data.getCommand()
                self.stateData = data.getStateData()
            except Exception as e:
                self.hasError = True
    
    def __str__(self):
        return f"ActuatorData: name={self.name}, typeID={self.typeID}, value={self.value}, " \
               f"command={self.command}, stateData={self.stateData}"