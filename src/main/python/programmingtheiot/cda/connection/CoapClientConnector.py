#####
# 
# This class is part of the Programming the Internet of Things project.
# 
# It is provided as a simple shell to guide the student and assist with
# implementation for the Programming the Internet of Things exercises,
# and designed to be modified by the student as needed.
#

import asyncio
import logging
import socket
import traceback

import programmingtheiot.common.ConfigConst as ConfigConst

from aiocoap import Context, Message, NON, CON, Code

from programmingtheiot.common.ConfigUtil import ConfigUtil
from programmingtheiot.common.ResourceNameEnum import ResourceNameEnum
from programmingtheiot.common.IDataMessageListener import IDataMessageListener
from programmingtheiot.common.DataUtil import DataUtil
from programmingtheiot.cda.connection.IRequestResponseClient import IRequestResponseClient


class CoapClientConnector(IRequestResponseClient):
    """
    Implementación de un cliente CoAP utilizando aiocoap.
    """

    def __init__(self, dataMsgListener: IDataMessageListener = None):
        self.config = ConfigUtil()
        self.dataMsgListener = dataMsgListener
        self.enableConfirmedMsgs = False
        self.coapClient = None
        self.observeRequests = {}

        self.host = self.config.getProperty(
            ConfigConst.COAP_GATEWAY_SERVICE,
            ConfigConst.HOST_KEY,
            ConfigConst.DEFAULT_HOST
        )
        self.port = self.config.getInteger(
            ConfigConst.COAP_GATEWAY_SERVICE,
            ConfigConst.PORT_KEY,
            ConfigConst.DEFAULT_COAP_PORT
        )
        self.uriPath = f"coap://{self.host}:{self.port}/"

        logging.info('\tHost:Port: %s:%s', self.host, str(self.port))

        self.includeDebugLogDetail = True

        try:
            tmpHost = socket.gethostbyname(self.host)

            if tmpHost:
                self.host = tmpHost
                self._initClient()
            else:
                logging.error("No se pudo resolver el host: " + self.host)

        except socket.gaierror:
            logging.info("Fallo al resolver el host: " + self.host)

    def _initClient(self):
        asyncio.get_event_loop().run_until_complete(self._initClientContext())

    async def _initClientContext(self):
        try:
            logging.info("Creando cliente CoAP para URI: " + self.uriPath)
            self.coapClient = await Context.create_client_context()
            logging.info("Cliente CoAP creado correctamente.")
        except Exception as e:
            logging.error("Fallo al crear el cliente CoAP.")
            traceback.print_exception(type(e), e, e.__traceback__)

    def sendDiscoveryRequest(self, timeout: int = IRequestResponseClient.DEFAULT_TIMEOUT) -> bool:
        logging.info("sendDiscoveryRequest() invocado.")
        return self.sendGetRequest(
            resource=None,
            name='.well-known/core',
            enableCON=False,
            timeout=timeout
        )

    def sendDeleteRequest(self, resource: ResourceNameEnum = None, name: str = None,
                          enableCON: bool = False, timeout: int = IRequestResponseClient.DEFAULT_TIMEOUT) -> bool:
        logging.info("sendDeleteRequest() invocado.")
        return False

    def sendGetRequest(self, resource: ResourceNameEnum = None, name: str = None,
                       enableCON: bool = False, timeout: int = IRequestResponseClient.DEFAULT_TIMEOUT) -> bool:
        if resource or name:
            resourcePath = self._createResourcePath(resource, name)
            fullUri = f"coap://{self.host}:{self.port}/{resourcePath}"
            logging.info("Issuing Async GET to path: " + fullUri)

            asyncio.get_event_loop().run_until_complete(
                self._handleGetRequest(resourcePath=fullUri, enableCON=enableCON)
            )
            return True
        else:
            logging.warning("No path provided for GET request.")
            return False

    async def _handleGetRequest(self, resourcePath: str = None, enableCON: bool = False):
        try:
            msgType = CON if enableCON else NON

            msg = Message(mtype=msgType, code=Code.GET, uri=resourcePath)
            req = self.coapClient.request(msg)
            responseData = await req.response

            self._onGetResponse(responseData)
        except Exception as e:
            logging.warning("Fallo al procesar la solicitud GET para la ruta: " + str(resourcePath))
            traceback.print_exception(type(e), e, e.__traceback__)

    def _onGetResponse(self, response):
        if not response:
            logging.warning('Async GET response invalid. Ignoring.')
            return

        logging.info('Async GET response received.')

        jsonData = response.payload.decode("utf-8")

        try:
            # Extrae el tipo de recurso del path si está presente
            if hasattr(response, 'requested_path') and len(response.requested_path) >= 3:
                dataType = response.requested_path[2]
            else:
                dataType = ""

            if dataType == ConfigConst.ACTUATOR_CMD:
                logging.info("ActuatorData recibido: %s", jsonData)
                try:
                    ad = DataUtil().jsonToActuatorData(jsonData)
                    if self.dataMsgListener:
                        self.dataMsgListener.handleActuatorCommandMessage(ad)
                except Exception:
                    logging.warning("Fallo al decodificar ActuatorData. Ignorado: %s", jsonData)
            else:
                logging.info("Datos recibidos: %s", jsonData)
        except Exception as e:
            logging.warning("Error procesando la respuesta GET.")
            traceback.print_exception(type(e), e, e.__traceback__)

    def sendPostRequest(self, resource: ResourceNameEnum = None, name: str = None,
                        enableCON: bool = False, payload: str = None,
                        timeout: int = IRequestResponseClient.DEFAULT_TIMEOUT) -> bool:
        logging.info("sendPostRequest() invocado.")
        return False

    def sendPutRequest(self, resource: ResourceNameEnum = None, name: str = None,
                       enableCON: bool = False, payload: str = None,
                       timeout: int = IRequestResponseClient.DEFAULT_TIMEOUT) -> bool:
        logging.info("sendPutRequest() invocado.")
        return False

    def setDataMessageListener(self, listener: IDataMessageListener = None) -> bool:
        logging.info("setDataMessageListener() invocado.")
        self.dataMsgListener = listener
        return True

    def startObserver(self, resource: ResourceNameEnum = None, name: str = None,
                      ttl: int = IRequestResponseClient.DEFAULT_TTL) -> bool:
        logging.info("startObserver() invocado.")
        return False

    def stopObserver(self, resource: ResourceNameEnum = None, name: str = None,
                     timeout: int = IRequestResponseClient.DEFAULT_TIMEOUT) -> bool:
        logging.info("stopObserver() invocado.")
        return False

    def _createResourcePath(self, resource: ResourceNameEnum = None, name: str = None) -> str:
        resourcePath = ""
        hasResource = False

        if resource:
            resourcePath += resource.value
            hasResource = True

        if name:
            if hasResource:
                resourcePath += '/'
            resourcePath += name

        return resourcePath
