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
from programmingtheiot.common.ISystemPerformanceDataListener import ISystemPerformanceDataListener


from programmingtheiot.data.DataUtil import DataUtil
from programmingtheiot.data.SystemPerformanceData import SystemPerformanceData


class GetSystemPerformanceResourceHandler(Resource, ISystemPerformanceDataListener):
    """
    Recurso CoAP observable que devuelve SystemPerformanceData actualizado.
    """


    def __init__(self, name: str = ConfigConst.SYSTEM_PERF_MSG, coap_server=None):
        super(GetSystemPerformanceResourceHandler, self).__init__(
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


        self.sysPerfData = None
        self.dataUtil = DataUtil()


        # Mensaje de prueba por defecto
        self.payload = "GetSysPerfData"


        logging.info("GetSystemPerformanceResourceHandler initialized.")


    def render_GET_advanced(self, request, response):
        logging.debug("GET request received for SystemPerformanceData.")


        if request:
            response.code = defines.Codes.CONTENT.number


            if not self.sysPerfData:
                logging.warning("No system performance data available.")
                response.code = defines.Codes.EMPTY.number
                self.sysPerfData = SystemPerformanceData()


            jsonData = self.dataUtil.systemPerformanceDataToJson(self.sysPerfData)


            response.payload = (defines.Content_types["application/json"], jsonData)
            response.max_age = self.pollCycles


            # Esto indica si el recurso ha cambiado desde la última notificación.
            self.changed = False


        return self, response


    def onSystemPerformanceDataUpdate(self, data: SystemPerformanceData) -> bool:
        """
        Método que actualiza el recurso con nuevos datos del sistema.
        """
        if data:
            logging.debug("Actualizando SystemPerformanceData en recurso CoAP.")
            self.sysPerfData = data
            self.changed = True  # Permite notificar a observadores
            return True


        logging.warning("Intento de actualización con datos vacíos.")
        return False
