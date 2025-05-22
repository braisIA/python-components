#####
#
# This class is part of the Programming the Internet of Things
# project, and is available via the MIT License, which can be
# found in the LICENSE file at the top level of this repository.
#
# Copyright (c) 2020 by Andrew D. King
#


import logging
import traceback


from threading import Thread
from time import sleep


from coapthon.server.coap import CoAP
from coapthon.resources.resource import Resource


import programmingtheiot.common.ConfigConst as ConfigConst


from programmingtheiot.common.ConfigUtil import ConfigUtil
from programmingtheiot.common.ResourceNameEnum import ResourceNameEnum


from programmingtheiot.common.IDataMessageListener import IDataMessageListener
from programmingtheiot.cda.connection.handlers.GetTelemetryResourceHandler import GetTelemetryResourceHandler
from programmingtheiot.cda.connection.handlers.UpdateActuatorResourceHandler import UpdateActuatorResourceHandler
from programmingtheiot.cda.connection.handlers.GetSystemPerformanceResourceHandler import GetSystemPerformanceResourceHandler


class CoapServerAdapter():
    """
    Definition for a CoAP communications server, with embedded test functions.
    """


    def __init__(self, dataMsgListener: IDataMessageListener = None):
        self.config = ConfigUtil()
        self.dataMsgListener = dataMsgListener
        self.enableConfirmedMsgs = False


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


        self.coapServer = None
        self.coapServerTask = None
        self.listenTimeout = 30  # used by CoAPthon3


        logging.info("CoAP server configured for host and port: coap://%s:%s", self.host, str(self.port))


        self._initServer()


    def _initServer(self):
        # Initialize the CoAP server with default handlers (none yet)
        class CoapResourceServer(CoAP):
            def __init__(self, host, port):
                CoAP.__init__(self, (host, port))
                logging.info("CoAP server initialized on %s:%s", host, port)


        try:
            self.coapServer = CoapResourceServer(self.host, self.port)

            # Add actuator resource handler(s)
            humidifierResource = UpdateActuatorResourceHandler(dataMsgListener=self.dataMsgListener)
            self.addResource(
                resourcePath=ResourceNameEnum.CDA_ACTUATOR_CMD_RESOURCE,
                endName=ConfigConst.HUMIDIFIER_ACTUATOR_NAME,
                resource=humidifierResource
            )

            # Add system performance resource handler
            sysPerfResource = GetSystemPerformanceResourceHandler()
            self.addResource(
                resourcePath=ResourceNameEnum.CDA_SYSTEM_PERF_MSG_RESOURCE,
                resource=sysPerfResource
            )

            # Register callbacks with dataMsgListener
            if self.dataMsgListener is not None:
                self.dataMsgListener.setSystemPerformanceDataListener(listener=sysPerfResource)

            logging.info("Created CoAP server with default resources.")

        except Exception as e:
            traceback.print_exception(type(e), e, e.__traceback__)
            logging.warning("Failed to create CoAP server.")


    def _runServer(self):
        try:
            self.coapServer.listen(self.listenTimeout)
        except Exception as e:
            traceback.print_exception(type(e), e, e.__traceback__)
            logging.warning("Failed to run server.")


    def addResource(self, resourcePath: ResourceNameEnum = None, endName: str = None, resource: Resource = None):
        """
        Add a resource handler to the CoAP server.
        Supports nested resource paths by splitting the URI and registering accordingly.
        """
        if resourcePath and resource:
            # Compose the URI path
            uriPath = resourcePath.value
            if endName:
                uriPath = uriPath + '/' + endName

            # Clean and split path into segments
            trimmedUriPath = uriPath.strip("/")
            resourceList = trimmedUriPath.split("/")

            resourceTree = None
            registrationPath = ""
            generationCount = 0

            for resourceName in resourceList:
                generationCount += 1
                registrationPath += "/" + resourceName

                try:
                    resourceTree = self.coapServer.root[registrationPath]
                except KeyError:
                    resourceTree = None

            # If the resource does not already exist in the tree, add it
            if not resourceTree:
                if len(resourceList) != generationCount:
                    # Intermediate resource, do not register yet
                    return None
                # Set the resource name and path
                if endName:
                    resource.name = endName
                else:
                    resource.name = resourceList[-1]
                resource.path = registrationPath
                self.coapServer.root[registrationPath] = resource
                logging.info(f"Resource added at path: {registrationPath}")
            else:
                logging.warning(f"Resource already exists at path: {registrationPath}")
        else:
            logging.warning("No resource or resourcePath provided for addResource.")


    def startServer(self):
        if self.coapServer:
            logging.info("Starting CoAP server...")


            if self.coapServerTask and self.coapServerTask.is_alive():
                self.stopServer()
                self.coapServerTask = None


            self.coapServerTask = Thread(target=self._runServer)
            self.coapServerTask.setDaemon(True)
            self.coapServerTask.start()


            logging.info("\n\n***** CoAP server started. *****\n\n")
        else:
            logging.warning("CoAP server not yet initialized (shouldn't happen).")


    def stopServer(self):
        if self.coapServer:
            logging.info("Stopping CoAP server...")


            self.coapServer.close()
            self.coapServerTask.join(5)
        else:
            logging.warning("CoAP server not yet initialized (shouldn't happen).")


    def setDataMessageListener(self, listener: IDataMessageListener = None) -> bool:
        if listener:
            self.dataMsgListener = listener
            logging.info("Data message listener set.")
            return True
        return False



