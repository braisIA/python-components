#####
# 
# This class is part of the Programming the Internet of Things project.
# 
# It is provided as a simple shell to guide the student and assist with
# implementation for the Programming the Internet of Things exercises,
# and designed to be modified by the student as needed.
#

import logging
import random

from programmingtheiot.data.ActuatorData import ActuatorData
from programmingtheiot.cda.sim.BaseActuatorSimTask import BaseActuatorSimTask
import programmingtheiot.common.ConfigConst as ConfigConst

class HvacActuatorSimTask(BaseActuatorSimTask):
	"""
	Simulación de un actuador HVAC (calefacción, ventilación y aire acondicionado).
	"""

	def __init__(self):
		super(HvacActuatorSimTask, self).__init__(
			name = ConfigConst.HVAC_ACTUATOR_NAME,
			typeID = ConfigConst.HVAC_ACTUATOR_TYPE,
			simpleName = "HVAC"
		)

		