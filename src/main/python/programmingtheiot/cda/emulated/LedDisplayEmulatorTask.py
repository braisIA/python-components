#####
# 
# This class is part of the Programming the Internet of Things project.
# 
# It is provided as a simple shell to guide the student and assist with
# implementation for the Programming the Internet of Things exercises,
# and designed to be modified by the student as needed.
#

import logging
import programmingtheiot.common.ConfigConst as ConfigConst
from programmingtheiot.common.ConfigUtil import ConfigUtil
from programmingtheiot.cda.sim.BaseActuatorSimTask import BaseActuatorSimTask
from pisense import SenseHAT

class LedDisplayEmulatorTask(BaseActuatorSimTask):
    """
    Emulador para el actuador de pantalla LED.
    """

    def __init__(self):
        super(LedDisplayEmulatorTask, self).__init__(
            name = ConfigConst.LED_ACTUATOR_NAME,
            typeID = ConfigConst.LED_DISPLAY_ACTUATOR_TYPE,
            simpleName = "LED_Display"
        )

        # Obtener si se debe emular el hardware desde la configuración
        enableEmulation = ConfigUtil().getBoolean(ConfigConst.CONSTRAINED_DEVICE, ConfigConst.ENABLE_EMULATOR_KEY)

        # Inicializar SenseHAT en modo emulación si enableEmulation es True
        self.sh = SenseHAT(emulate = enableEmulation)

    def _activateActuator(self, val: float = ConfigConst.DEFAULT_VAL, stateData: str = None) -> int:
        """ Activa el actuador de la pantalla LED y despliega los datos de estado """
        if self.sh.screen:
            if stateData:
                self.sh.screen.scroll_text(stateData, size = 8)
            else:
                logging.warning("No state data provided to display.")
            return 0
        else:
            logging.warning("No SenseHAT LED screen instance to write.")
            return -1

    def _deactivateActuator(self, val: float = ConfigConst.DEFAULT_VAL, stateData: str = None) -> int:
        """ Desactiva el actuador de la pantalla LED y limpia la pantalla """
        if self.sh.screen:
            self.sh.screen.clear()
            return 0
        else:
            logging.warning("No SenseHAT LED screen instance to clear / close.")
            return -1
