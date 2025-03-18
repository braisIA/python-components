#####
# 
# This class is part of the Programming the Internet of Things
# project, and is available via the MIT License, which can be
# found in the LICENSE file at the top level of this repository.
# 
# You may find it more helpful to your design to adjust the
# functionality, constants and interfaces (if there are any)
# provided within in order to meet the needs of your specific
# Programming the Internet of Things project.
# 

import logging

from time import sleep
from programmingtheiot.common.ConfigUtil import ConfigUtil
from programmingtheiot.common.ConfigConst import CONSTRAINED_DEVICE, POLL_CYCLES_KEY, DEFAULT_POLL_CYCLES, DEVICE_LOCATION_ID_KEY, NOT_SET


logging.basicConfig(format = '%(asctime)s:%(name)s:%(levelname)s:%(message)s', level = logging.DEBUG)


class SystemPerformanceManager:
    """
    Clase para gestionar el rendimiento del sistema en un dispositivo con recursos limitados.
    """

    def __init__(self):
        """
        Constructor de la clase. Configura los parámetros iniciales.
        """
        self.logger = logging.getLogger(__name__)
        configUtil = ConfigUtil()

        self.pollRate = configUtil.getInteger(
            section=CONSTRAINED_DEVICE,
            key=POLL_CYCLES_KEY,
            defaultVal=DEFAULT_POLL_CYCLES
        )

        self.locationID = configUtil.getProperty(
            section=CONSTRAINED_DEVICE,
            key=DEVICE_LOCATION_ID_KEY,
            defaultVal=NOT_SET
        )

        if self.pollRate <= 0:
            self.pollRate = DEFAULT_POLL_CYCLES

        self.dataMsgListener = None
        self.logger.info("SystemPerformanceManager inicializado con pollRate=%d y locationID='%s'.",
                         self.pollRate, self.locationID)

    def startManager(self):
        """
        Inicia el gestor de rendimiento del sistema.
        """
        self.logger.info("Started SystemPerformanceManager.")

    def stopManager(self):
        """
        Detiene el gestor de rendimiento del sistema.
        """
        self.logger.info("Stopped SystemPerformanceManager.")
        

class ConstrainedDeviceApp():
	"""
	Definition of the ConstrainedDeviceApp class.
	
	"""
	
	def __init__(self):
		"""
		Initialization of class.
		
		@param path The name of the resource to apply to the URI.
		"""
		self.logger = logging.getLogger(__name__)
        
		self.logger.info("Initializing CDA...")
  
		self.sysPerfManager = SystemPerformanceManager()

	def startApp(self):
		"""
		Start the CDA. Calls startManager() on the device data manager instance.
		
		"""
		self.logger.info("Starting CDA...")
  
		self.sysPerfManager.startManager()
		
		self.logger.info("CDA started.")
  


	def stopApp(self, code: int):
		"""
		Stop the CDA. Calls stopManager() on the device data manager instance.
		
		"""
		self.logger.info("CDA stopping...")
  
		self.sysPerfManager.stopManager()
		
		self.logger.info("CDA stopped with exit code %s.", str(code))
		
	def parseArgs(self, args):
		"""
		Parse command line args.
		
		@param args The arguments to parse.
		"""
		logging.info("Parsing command line args...")


def main():
	"""
	Main function definition for running client as application.
	
	Current implementation runs for 35 seconds then exits.
	"""
	cda = ConstrainedDeviceApp()
	cda.startApp()
	
	# run for 65 seconds - this can be changed as needed
	sleep(65)
	
	# optionally stop the app - this can be removed if needed
	cda.stopApp(0)

if __name__ == '__main__':
	"""
	Attribute definition for when invoking as app via command line
	
	"""
	main()
	