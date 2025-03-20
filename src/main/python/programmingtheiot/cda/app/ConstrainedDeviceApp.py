import logging
from time import sleep

from programmingtheiot.common.ConfigUtil import ConfigUtil
from programmingtheiot.common.ConfigConst import CONSTRAINED_DEVICE, POLL_CYCLES_KEY, DEFAULT_POLL_CYCLES, DEVICE_LOCATION_ID_KEY, NOT_SET
from programmingtheiot.cda.app.DeviceDataManager import DeviceDataManager

logging.basicConfig(format='%(asctime)s:%(name)s:%(levelname)s:%(message)s', level=logging.DEBUG)

class ConstrainedDeviceApp:
    """
    Clase principal de la aplicación para dispositivos con recursos limitados.
    """

    def __init__(self):
        """
        Inicialización de la aplicación.
        """
        self.logger = logging.getLogger(__name__)
        self.logger.info("Inicializando ConstrainedDeviceApp...")

        # Reemplazamos SystemPerformanceManager con DeviceDataManager
        self.devDataMgr = DeviceDataManager()

    def startApp(self):
        """
        Inicia la aplicación. Llama a startManager() en DeviceDataManager.
        """
        self.logger.info("Iniciando ConstrainedDeviceApp...")
        self.devDataMgr.startManager()
        self.logger.info("ConstrainedDeviceApp iniciada.")

    def stopApp(self, code: int):
        """
        Detiene la aplicación. Llama a stopManager() en DeviceDataManager.
        """
        self.logger.info("Deteniendo ConstrainedDeviceApp...")
        self.devDataMgr.stopManager()
        self.logger.info("ConstrainedDeviceApp detenida con código de salida %s.", str(code))

    def parseArgs(self, args):
        """
        Analiza argumentos de línea de comandos.
        """
        logging.info("Analizando argumentos de línea de comandos...")

def main():
    """
    Función principal de la aplicación.
    """
    cda = ConstrainedDeviceApp()
    cda.startApp()

    # Ejecutar indefinidamente si está configurado en el archivo de configuración
    runForever = ConfigUtil().getBoolean(CONSTRAINED_DEVICE, "runForever", defaultVal=False)

    if runForever:
        while True:
            sleep(5)
    else:
        sleep(65)  # Puede hacerse configurable
        cda.stopApp(0)

if __name__ == '__main__':
    main()
