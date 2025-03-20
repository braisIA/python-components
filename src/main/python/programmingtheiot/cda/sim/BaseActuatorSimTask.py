#####
# 
# This class is part of the Programming the Internet of Things project.
# 
# It is provided as a simple shell to guide the student and assist with
# implementation for the Programming the Internet of Things exercises,
# and designed to be modified by the student as needed.
#

import logging
import programmingtheiot.common.ConfigConst as ConfigConst
from programmingtheiot.data.ActuatorData import ActuatorData

class BaseActuatorSimTask():
    """
    Base class for actuator simulation tasks.
    """

    def __init__(self, name: str = ConfigConst.NOT_SET, typeID: int = ConfigConst.DEFAULT_ACTUATOR_TYPE, simpleName: str = "Actuator"):
        """
        Constructor initializes the actuator simulation task.
        """
        self.latestActuatorResponse = ActuatorData(typeID=typeID, name=name)
        self.latestActuatorResponse.setAsResponse()

        self.name = name
        self.typeID = typeID
        self.simpleName = simpleName
        self.lastKnownCommand = ConfigConst.DEFAULT_COMMAND
        self.lastKnownValue = ConfigConst.DEFAULT_VAL

    def getLatestActuatorResponse(self) -> ActuatorData:
        """
        Returns the latest ActuatorData response.
        """
        return self.latestActuatorResponse

    def getSimpleName(self) -> str:
        """
        Returns the simple name of the actuator.
        """
        return self.simpleName

    def updateActuator(self, data: ActuatorData) -> ActuatorData:
        """
        Updates the actuator state based on the received ActuatorData.
        """
        if data and self.typeID == data.getTypeID():
            statusCode = ConfigConst.DEFAULT_STATUS

            curCommand = data.getCommand()
            curVal = data.getValue()

            # Check if the command and value are the same as the last known values
            if curCommand == self.lastKnownCommand and curVal == self.lastKnownValue:
                logging.debug("Command and value are the same as the last known. Ignoring: %s %s", str(curCommand), str(curVal))
            else:
                logging.debug("New actuator command and value to be applied: %s %s", str(curCommand), str(curVal))

                if curCommand == ConfigConst.COMMAND_ON:
                    logging.info("Activating actuator...")
                    statusCode = self._activateActuator(val=data.getValue(), stateData=data.getStateData())
                elif curCommand == ConfigConst.COMMAND_OFF:
                    logging.info("Deactivating actuator...")
                    statusCode = self._deactivateActuator(val=data.getValue(), stateData=data.getStateData())
                else:
                    logging.warning("Unknown ActuatorData command. Ignoring: %s", str(curCommand))
                    statusCode = -1

                # Update the last known command and value
                self.lastKnownCommand = curCommand
                self.lastKnownValue = curVal

                # Create the ActuatorData response
                actuatorResponse = ActuatorData()
                actuatorResponse.updateData(data)
                actuatorResponse.setStatusCode(statusCode)
                actuatorResponse.setAsResponse()

                self.latestActuatorResponse.updateData(actuatorResponse)

                return actuatorResponse

        return None

    def _activateActuator(self, val: float = ConfigConst.DEFAULT_VAL, stateData: str = None) -> int:
        """
        Logs activation message. Can be overridden by subclasses for specific actuator functionality.
        """
        msg = "\n*******"
        msg += "\n* O N *"
        msg += "\n*******"
        msg += f"\n{self.name} VALUE -> {val}\n======="

        logging.info("Simulating actuator %s ON: %s", self.name, msg)

        return 0

    def _deactivateActuator(self, val: float = ConfigConst.DEFAULT_VAL, stateData: str = None) -> int:
        """
        Logs deactivation message. Can be overridden by subclasses for specific actuator functionality.
        """
        msg = "\n*******"
        msg += "\n* OFF *"
        msg += "\n*******"

        logging.info("Simulating actuator %s OFF: %s", self.name, msg)

        return 0
