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
    Representa un comando de actuador con soporte para valores tipo float
    y mensajes de estado. Compatible con serialización JSON.
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
        self.updateTimeStamp()

    def getCommand(self) -> int:
        return self.command

    def setCommand(self, command: int):
        self.command = command
        self.updateTimeStamp()

    def getStateData(self) -> str:
        return self.stateData

    def setStateData(self, stateData: str):
        self.stateData = stateData
        self.updateTimeStamp()

    def _handleUpdateData(self, data):
        if isinstance(data, ActuatorData):
            self.value = data.getValue()
            self.command = data.getCommand()
            self.stateData = data.getStateData()
        else:
            raise ValueError("Expected an ActuatorData instance.")

    def __str__(self):
        return (
            f"ActuatorData [ name = {self.name}, typeID = {self.typeID}, "
            f"value = {self.value}, command = {self.command}, "
            f"stateData = '{self.stateData}', timestamp = {self.timeStamp} ]"
        )