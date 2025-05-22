#####
#
# This class is part of the Programming the Internet of Things
# project, and is available via the MIT License, which can be
# found in the LICENSE file at the top level of this repository.
#
# Copyright (c) 2020 by Andrew D. King
#####


import logging


from coapthon import defines
from coapthon.resources.resource import Resource


from programmingtheiot.common.IDataMessageListener import IDataMessageListener
from programmingtheiot.data.DataUtil import DataUtil
from programmingtheiot.data.ActuatorData import ActuatorData


class UpdateActuatorResourceHandler(Resource):
    """
    Standard resource that will handle an incoming actuation command,
    and return the command response.


    This implementation is based on CoAPthon3.
    """


    def __init__(self, name="UpdateActuator", dataMsgListener: IDataMessageListener = None):
        super(UpdateActuatorResourceHandler, self).__init__(name)
        self.dataMsgListener = dataMsgListener
        self.dataUtil = DataUtil()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.pollCycles = 60  # Optional: how long response should be cached


    def render_PUT_advanced(self, request, response):
        self.logger.info("PUT request received on UpdateActuatorResourceHandler.")
       
        if request:
            try:
                requestPayload = request.payload
                self.logger.debug(f"Payload received: {requestPayload}")


                # Convert JSON payload to ActuatorData
                actuatorCmdData = self.dataUtil.jsonToActuatorData(requestPayload)


                # Handle the actuation command
                response.payload = self._createResponse(response=response, data=actuatorCmdData)
                response.max_age = self.pollCycles
            except Exception as e:
                self.logger.warning(f"Error handling PUT request: {e}")
                response.code = defines.Codes.BAD_REQUEST.number
        else:
            self.logger.warning("Received null request.")
            response.code = defines.Codes.BAD_REQUEST.number


        return self, response


    def _createResponse(self, response=None, data: ActuatorData = None) -> str:
        # Get response from listener
        actuatorResponseData = self.dataMsgListener.handleActuatorCommandMessage(data) if self.dataMsgListener else None


        if not actuatorResponseData:
            self.logger.warning("ActuatorData response is None. Sending fallback error response.")
            actuatorResponseData = ActuatorData()
            actuatorResponseData.updateData(data)
            actuatorResponseData.setAsResponse()
            actuatorResponseData.setStatusCode(-1)
            response.code = defines.Codes.PRECONDITION_FAILED.number
        else:
            response.code = defines.Codes.CHANGED.number


        jsonData = self.dataUtil.actuatorDataToJson(actuatorResponseData)
        return jsonData
