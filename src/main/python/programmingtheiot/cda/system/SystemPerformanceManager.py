#####
# 
# This class is part of the Programming the Internet of Things project.
# 
# It is provided as a simple shell to guide the student and assist with
# implementation for the Programming the Internet of Things exercises,
# and designed to be modified by the student as needed.
#

import logging

from apscheduler.schedulers.background import BackgroundScheduler

import programmingtheiot.common.ConfigConst as ConfigConst

from programmingtheiot.common.ConfigUtil import ConfigUtil
from programmingtheiot.common.IDataMessageListener import IDataMessageListener

from programmingtheiot.cda.system.SystemCpuUtilTask import SystemCpuUtilTask
from programmingtheiot.cda.system.SystemMemUtilTask import SystemMemUtilTask

from programmingtheiot.data.SystemPerformanceData import SystemPerformanceData

class SystemPerformanceManager(object):
    """
    Shell representation of class for student implementation.
    """

    def __init__(self):
        # Configuración y valores iniciales
        configUtil = ConfigUtil()

        # Obtener el intervalo de sondeo (poll rate) de la configuración
        self.pollRate = configUtil.getInteger(
            section=ConfigConst.CONSTRAINED_DEVICE, 
            key=ConfigConst.POLL_CYCLES_KEY, 
            defaultVal=ConfigConst.DEFAULT_POLL_CYCLES
        )

        # Obtener el ID de ubicación de la configuración
        self.locationID = configUtil.getProperty(
            section=ConfigConst.CONSTRAINED_DEVICE, 
            key=ConfigConst.DEVICE_LOCATION_ID_KEY, 
            defaultVal=ConfigConst.NOT_SET
        )

        if self.pollRate <= 0:
            self.pollRate = ConfigConst.DEFAULT_POLL_CYCLES

        self.dataMsgListener = None

        # Inicialización del programador
        self.scheduler = BackgroundScheduler()
        self.scheduler.add_job(self.handleTelemetry, 'interval', seconds=self.pollRate)

        # Instanciar las tareas de utilización de CPU y memoria
        self.cpuUtilTask = SystemCpuUtilTask()
        self.memUtilTask = SystemMemUtilTask()

    def handleTelemetry(self):
        # Obtener los valores de utilización de CPU y memoria
        cpuUtilPct = self.cpuUtilTask.getTelemetryValue()
        memUtilPct = self.memUtilTask.getTelemetryValue()

        # Crear una instancia de SystemPerformanceData
        systemData = SystemPerformanceData(cpuUtilPct, memUtilPct)

        # Registrar los resultados
        logging.debug(
            'CPU utilization is %s percent, and memory utilization is %s percent.',
            str(cpuUtilPct), str(memUtilPct)
        )

        # Si se ha configurado un listener de mensajes de datos, notificarlo
        if self.dataMsgListener:
            self.dataMsgListener.onDataMessage(systemData)

    def setDataMessageListener(self, listener: IDataMessageListener) -> bool:
        """
        Set the data message listener to handle system performance data.
        """
        self.dataMsgListener = listener
        return True

    def startManager(self):
        logging.info("Starting SystemPerformanceManager...")

        if not self.scheduler.running:
            self.scheduler.start()
            logging.info("Started SystemPerformanceManager.")
        else:
            logging.warning("SystemPerformanceManager scheduler already started. Ignoring.")

    def stopManager(self):
        logging.info("Stopping SystemPerformanceManager...")

        try:
            self.scheduler.shutdown()
            logging.info("Stopped SystemPerformanceManager.")
        except:
            logging.warning("SystemPerformanceManager scheduler already stopped. Ignoring.")
