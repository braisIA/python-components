#####
# 
# This class is part of the Programming the Internet of Things project.
# 
# It is provided as a simple shell to guide the student and assist with
# implementation for the Programming the Internet of Things exercises,
# and designed to be modified by the student as needed.
#

import psutil
import logging
from programmingtheiot.cda.system.BaseSystemUtilTask import BaseSystemUtilTask

class SystemMemUtilTask(BaseSystemUtilTask):
    """
    Shell representation of class for student implementation.
    """

    def __init__(self):
        super().__init__()
        # Configurar el logger si es necesario
        self.logger = logging.getLogger(__name__)

    def getTelemetryValue(self) -> float:
        """
        Obtiene el valor de utilización de la memoria del sistema.
        Devuelve un valor flotante que representa el porcentaje de memoria usada.
        """
        try:
            # Obtener el uso de memoria del sistema
            mem = psutil.virtual_memory()  # Devuelve un objeto con varios detalles
            mem_usage_percent = mem.percent  # El porcentaje de memoria usada
            return mem_usage_percent

        except Exception as e:
            # Manejo de errores: loguear el error si ocurre alguno
            self.logger.error(f"Error al obtener la utilización de la memoria: {str(e)}")
            return 0.0  # Devolver 0 si hay un error, para evitar retornar None

