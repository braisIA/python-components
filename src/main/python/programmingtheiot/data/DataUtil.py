import json
import logging

from decimal import Decimal
from json import JSONEncoder

from programmingtheiot.data.ActuatorData import ActuatorData
from programmingtheiot.data.SensorData import SensorData
from programmingtheiot.data.SystemPerformanceData import SystemPerformanceData

class DataUtil():
	"""
	Clase de utilidad para serialización y deserialización de datos IoT.
	"""

	def __init__(self, encodeToUtf8=False):
		self.encodeToUtf8 = encodeToUtf8
		logging.info("Instancia de DataUtil creada.")

	# ---- CONVERSIONES DE OBJETO A JSON ----

	def actuatorDataToJson(self, data: ActuatorData = None, useDecForFloat: bool = False):
		if not data:
			logging.debug("ActuatorData es None. Retornando string vacío.")
			return ""
		return self._generateJsonData(obj=data, useDecForFloat=useDecForFloat)

	def sensorDataToJson(self, data: SensorData = None, useDecForFloat: bool = False):
		if not data:
			logging.debug("SensorData es None. Retornando string vacío.")
			return ""
		return self._generateJsonData(obj=data, useDecForFloat=useDecForFloat)

	def systemPerformanceDataToJson(self, data: SystemPerformanceData = None, useDecForFloat: bool = False):
		if not data:
			logging.debug("SystemPerformanceData es None. Retornando string vacío.")
			return ""
		return self._generateJsonData(obj=data, useDecForFloat=useDecForFloat)

	# ---- CONVERSIONES DE JSON A OBJETO ----

	def jsonToActuatorData(self, jsonData: str = None, useDecForFloat: bool = False):
		if not jsonData:
			logging.warning("El JSON recibido es nulo o vacío.")
			return None
		jsonStruct = self._formatDataAndLoadDictionary(jsonData, useDecForFloat=useDecForFloat)
		ad = ActuatorData()
		self._updateIotData(jsonStruct, ad)
		return ad

	def jsonToSensorData(self, jsonData: str = None, useDecForFloat: bool = False):
		if not jsonData:
			logging.warning("El JSON recibido es nulo o vacío.")
			return None
		jsonStruct = self._formatDataAndLoadDictionary(jsonData, useDecForFloat=useDecForFloat)
		sd = SensorData()
		self._updateIotData(jsonStruct, sd)
		return sd

	def jsonToSystemPerformanceData(self, jsonData: str = None, useDecForFloat: bool = False):
		if not jsonData:
			logging.warning("El JSON recibido es nulo o vacío.")
			return None
		jsonStruct = self._formatDataAndLoadDictionary(jsonData, useDecForFloat=useDecForFloat)
		spd = SystemPerformanceData()
		self._updateIotData(jsonStruct, spd)
		return spd

	# ---- MÉTODOS PRIVADOS DE APOYO ----

	def _generateJsonData(self, obj, useDecForFloat: bool = False) -> str:
		jsonData = None

		if self.encodeToUtf8:
			jsonData = json.dumps(obj, cls=JsonDataEncoder).encode('utf8')
		else:
			jsonData = json.dumps(obj, cls=JsonDataEncoder, indent=4)

		if jsonData:
			jsonData = jsonData.replace("\'", "\"").replace('False', 'false').replace('True', 'true')

		return jsonData

	def _formatDataAndLoadDictionary(self, jsonData: str, useDecForFloat: bool = False) -> dict:
		jsonData = jsonData.replace("\'", "\"").replace('False', 'false').replace('True', 'true')
		if useDecForFloat:
			return json.loads(jsonData, parse_float=Decimal)
		else:
			return json.loads(jsonData)

	def _updateIotData(self, jsonStruct, obj):
		varStruct = vars(obj)
		for key in jsonStruct:
			if key in varStruct:
				setattr(obj, key, jsonStruct[key])
			else:
				logging.warning("Clave JSON no mapeada en el objeto: %s", key)

class JsonDataEncoder(JSONEncoder):
	"""
	Clase de conveniencia para codificar cualquier objeto como dict JSON.
	"""
	def default(self, o):
		return o.__dict__
