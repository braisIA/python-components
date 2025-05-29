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
        self.observeRequests = {}  # Map to store observe requests and their cancellation handles

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

    # --- MODIFICACIÓN: Soporte DELETE requests ---
    def sendDeleteRequest(self, resource: ResourceNameEnum = None, name: str = None,
                          enableCON: bool = False, timeout: int = IRequestResponseClient.DEFAULT_TIMEOUT) -> bool:
        if resource or name:
            resourcePath = self._createResourcePath(resource, name)
            fullUri = f"coap://{self.host}:{self.port}/{resourcePath}"
            logging.info("Issuing Async DELETE to path: " + fullUri)

            asyncio.get_event_loop().run_until_complete(
                self._handleDeleteRequest(resourcePath=fullUri, enableCON=enableCON)
            )
            return True
        else:
            logging.warning("Can't issue Async DELETE - no path or path list provided.")
            return False

    async def _handleDeleteRequest(self, resourcePath: str = None, enableCON: bool = False):
        try:
            msgType = CON if enableCON else NON

            msg = Message(mtype=msgType, code=Code.DELETE, uri=resourcePath)
            req = self.coapClient.request(msg)
            responseData = await req.response

            self._onDeleteResponse(responseData)

        except Exception as e:
            logging.warning("Failed to process DELETE request for path: " + str(resourcePath))
            traceback.print_exception(type(e), e, e.__traceback__)

    def _onDeleteResponse(self, response):
        if not response:
            logging.warning('DELETE response invalid. Ignoring.')
            return

        logging.info('DELETE response received: %s', response.payload.decode("utf-8") if response.payload else "No Payload")
    # --- FIN MODIFICACIÓN ---

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
        if resource or name:
            resourcePath = self._createResourcePath(resource, name)
            fullUri = f"coap://{self.host}:{self.port}/{resourcePath}"

            logging.info("Issuing Async POST to path: " + fullUri)

            asyncio.get_event_loop().run_until_complete(
                self._handlePostRequest(
                    resourcePath=fullUri,
                    payload=payload,
                    enableCON=enableCON
                )
            )
            return True
        else:
            logging.warning("Can't issue Async POST - no path or path list provided.")
            return False

    async def _handlePostRequest(self, resourcePath: str = None, payload: str = None, enableCON: bool = False):
        try:
            msgType = CON if enableCON else NON

            payloadBytes = b''
            if payload:
                payloadBytes = payload.encode('utf-8')

            msg = Message(mtype=msgType, payload=payloadBytes, code=Code.POST, uri=resourcePath)
            req = self.coapClient.request(msg)
            responseData = await req.response

            self._onPostResponse(responseData)

        except Exception as e:
            logging.warning("Failed to process POST request for path: " + str(resourcePath))
            traceback.print_exception(type(e), e, e.__traceback__)

    def _onPostResponse(self, response):
        if not response:
            logging.warning('POST response invalid. Ignoring.')
            return

        logging.info('POST response received: %s', response.payload.decode("utf-8"))

    # --- MODIFICACIÓN: Soporte PUT requests ---

    def sendPutRequest(self, resource: ResourceNameEnum = None, name: str = None,
                       enableCON: bool = False, payload: str = None,
                       timeout: int = IRequestResponseClient.DEFAULT_TIMEOUT) -> bool:
        if resource or name:
            resourcePath = self._createResourcePath(resource, name)
            fullUri = f"coap://{self.host}:{self.port}/{resourcePath}"

            logging.info("Issuing Async PUT to path: " + fullUri)

            asyncio.get_event_loop().run_until_complete(
                self._handlePutRequest(
                    resourcePath=fullUri,
                    payload=payload,
                    enableCON=enableCON
                )
            )
            return True
        else:
            logging.warning("Can't issue Async PUT - no path or path list provided.")
            return False

    async def _handlePutRequest(self, resourcePath: str = None, payload: str = None, enableCON: bool = False):
        try:
            msgType = CON if enableCON else NON

            payloadBytes = b''
            if payload:
                payloadBytes = payload.encode('utf-8')

            msg = Message(mtype=msgType, payload=payloadBytes, code=Code.PUT, uri=resourcePath)
            req = self.coapClient.request(msg)
            responseData = await req.response

            self._onPutResponse(responseData)

        except Exception as e:
            logging.warning("Failed to process PUT request for path: " + str(resourcePath))
            traceback.print_exception(type(e), e, e.__traceback__)

    def _onPutResponse(self, response):
        if not response:
            logging.warning('PUT response invalid. Ignoring.')
            return

        logging.info('PUT response received: %s', response.payload.decode("utf-8"))

    # --- FIN MODIFICACIÓN ---

    def setDataMessageListener(self, listener: IDataMessageListener = None) -> bool:
        logging.info("setDataMessageListener() invocado.")
        self.dataMsgListener = listener
        return True

    # --- IMPLEMENTACIÓN OBSERVE ---

    def startObserver(self, resource: ResourceNameEnum = None, name: str = None,
                      ttl: int = IRequestResponseClient.DEFAULT_TTL) -> bool:
        """
        Inicia la observación de un recurso CoAP.
        """
        if not (resource or name):
            logging.warning("No path provided for OBSERVE request.")
            return False

        resourcePath = self._createResourcePath(resource, name)
        fullUri = f"coap://{self.host}:{self.port}/{resourcePath}"

        if fullUri in self.observeRequests:
            logging.info(f"Already observing resource: {fullUri}")
            return True  # Ya está observando

        logging.info(f"Starting observation of resource: {fullUri}")

        # Lanzar tarea async para gestionar la observación
        async def observe_task():
            try:
                request = Message(code=Code.GET, uri=fullUri, observe=0)

                pr = self.coapClient.request(request)

                # Guardar el pr para cancelarlo luego si es necesario
                self.observeRequests[fullUri] = pr

                async for response in pr.observation:
                    self._onObserveNotification(response, resourcePath)

            except Exception as e:
                logging.warning(f"Error during observe on {fullUri}: {e}")
                traceback.print_exception(type(e), e, e.__traceback__)
                self.observeRequests.pop(fullUri, None)

        asyncio.ensure_future(observe_task())
        return True

    def stopObserver(self, resource: ResourceNameEnum = None, name: str = None,
                     timeout: int = IRequestResponseClient.DEFAULT_TIMEOUT) -> bool:
        """
        Detiene la observación de un recurso CoAP.
        """
        if not (resource or name):
            logging.warning("No path provided for stopObserver request.")
            return False

        resourcePath = self._createResourcePath(resource, name)
        fullUri = f"coap://{self.host}:{self.port}/{resourcePath}"

        if fullUri not in self.observeRequests:
            logging.info(f"No active observation for resource: {fullUri}")
            return False

        logging.info(f"Stopping observation of resource: {fullUri}")

        pr = self.observeRequests.pop(fullUri, None)
        if pr:
            pr.observation.cancel()
            return True
        else:
            return False

    def _onObserveNotification(self, response, resourcePath):
        if not response:
            logging.warning('Observe notification invalid. Ignoring.')
            return

        payloadStr = response.payload.decode("utf-8") if response.payload else ""
        logging.info(f"Observe notification received on {resourcePath}: {payloadStr}")

        # Manejar específicamente actualizaciones de actuadores
        try:
            # Extraer tipo recurso para decidir qué hacer
            pathParts = resourcePath.split('/')
            dataType = ""
            if len(pathParts) > 0:
                # El último componente puede ser el nombre o el tipo de recurso
                # Asumimos que es el segundo en la lista: por ejemplo /actuatorCmd
                dataType = pathParts[-1]

            if dataType == ConfigConst.ACTUATOR_CMD:
                try:
                    ad = DataUtil().jsonToActuatorData(payloadStr)
                    if self.dataMsgListener:
                        self.dataMsgListener.handleActuatorCommandMessage(ad)
                        logging.info("ActuatorData manejado desde notificación observe.")
                except Exception:
                    logging.warning(f"Error al decodificar ActuatorData desde notificación observe: {payloadStr}")
            else:
                # Para otros datos, simplemente loguear
                logging.info(f"Datos observe recibidos: {payloadStr}")
        except Exception as e:
            logging.warning("Error procesando la notificación observe.")
            traceback.print_exception(type(e), e, e.__traceback__)

    # --- FIN IMPLEMENTACIÓN OBSERVE ---

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
