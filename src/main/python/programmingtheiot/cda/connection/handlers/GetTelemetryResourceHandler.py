#####
#
# This class is part of the Programming the Internet of Things
# project, and is available via the MIT License, which can be
# found in the LICENSE file at the top level of this repository.
#
# Copyright (c) 2020 by Andrew D. King
#


import logging


from coapthon import defines
from coapthon.resources.resource import Resource


import programmingtheiot.common.ConfigConst as ConfigConst


from programmingtheiot.common.ConfigUtil import ConfigUtil
from programmingtheiot.common.ITelemetryDataListener import ITelemetryDataListener


from programmingtheiot.data.DataUtil import DataUtil
from programmingtheiot.data.SensorData import SensorData


class GetTelemetryResourceHandler(Resource, ITelemetryDataListener):
    """
    Recurso CoAP observable que devuelve datos de telemetría (SensorData) en formato JSON.
    """


    def __init__(self, name: str = ConfigConst.SENSOR_MSG, coap_server=None):
        super(GetTelemetryResourceHandler, self).__init__(
            name,
            coap_server,
            visible=True,
            observable=True,
            allow_children=True
        )


        self.pollCycles = ConfigUtil().getInteger(
            section=ConfigConst.CONSTRAINED_DEVICE,
            key=ConfigConst.POLL_CYCLES_KEY,
            defaultVal=ConfigConst.DEFAULT_POLL_CYCLES
        )


        self.sensorData = None
        self.dataUtil = DataUtil()


        # Mensaje de prueba por defecto
        self.payload = "GetSensorData"


        logging.info("GetTelemetryResourceHandler initialized.")


    def render_GET_advanced(self, request, response):
        logging.debug("GET request received for SensorData.")


        if request:
            response.code = defines.Codes.CONTENT.number


            if not self.sensorData:
                logging.warning("No sensor data available.")
                response.code = defines.Codes.EMPTY.number
                self.sensorData = SensorData()


            jsonData = self.dataUtil.sensorDataToJson(self.sensorData)


            response.payload = (defines.Content_types["application/json"], jsonData)
            response.max_age = self.pollCycles


            self.changed = False


        return self, response


    def onSensorDataUpdate(self, data: SensorData = None) -> bool:
        """
        Método que actualiza el recurso con nuevos datos de sensores.
        """
        if data:
            logging.debug("Actualizando SensorData en recurso CoAP.")
            self.sensorData = data
            self.changed = True  # Notifica a los observadores
            return True


        logging.warning("Intento de actualización con datos vacíos.")
        return False