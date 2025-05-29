# programmingtheiot/common/DataUtil.py

import json
import logging

from programmingtheiot.data.ActuatorData import ActuatorData
from programmingtheiot.data.SensorData import SensorData
from programmingtheiot.data.SystemPerformanceData import SystemPerformanceData

class DataUtil:
    def actuatorDataToJson(self, actuatorData: ActuatorData) -> str:
        try:
            data = {
                "name": actuatorData.getName(),
                "value": actuatorData.getValue(),
                "command": actuatorData.getCommand(),
                "stateData": actuatorData.getStateData(),
                "timeStamp": actuatorData.getTimeStamp()
            }
            return json.dumps(data)
        except Exception as e:
            logging.error("Error converting ActuatorData to JSON: %s", str(e))
            raise

    def jsonToActuatorData(self, jsonData: str) -> ActuatorData:
        try:
            data = json.loads(jsonData)
            ad = ActuatorData()
            ad.setName(data.get("name", ""))
            ad.setValue(data.get("value", 0.0))
            ad.setCommand(data.get("command", 0))
            ad.setStateData(data.get("stateData", ""))
            ad.setTimeStamp(data.get("timeStamp", None))
            return ad
        except Exception as e:
            logging.error("Error parsing ActuatorData JSON: %s", str(e))
            raise

    def sensorDataToJson(self, sensorData: SensorData) -> str:
        try:
            data = {
                "name": sensorData.getName(),
                "value": sensorData.getValue(),
                "timeStamp": sensorData.getTimeStamp()
            }
            return json.dumps(data)
        except Exception as e:
            logging.error("Error converting SensorData to JSON: %s", str(e))
            raise

    def jsonToSensorData(self, jsonData: str) -> SensorData:
        try:
            data = json.loads(jsonData)
            sd = SensorData()
            sd.setName(data.get("name", ""))
            sd.setValue(data.get("value", 0.0))
            sd.setTimeStamp(data.get("timeStamp", None))
            return sd
        except Exception as e:
            logging.error("Error parsing SensorData JSON: %s", str(e))
            raise

    def systemPerformanceDataToJson(self, sysPerfData: SystemPerformanceData) -> str:
        try:
            data = {
                "cpuUtil": sysPerfData.getCpuUtil(),
                "memUtil": sysPerfData.getMemoryUtil(),
                "timeStamp": sysPerfData.getTimeStamp()
            }
            return json.dumps(data)
        except Exception as e:
            logging.error("Error converting SystemPerformanceData to JSON: %s", str(e))
            raise

    def jsonToSystemPerformanceData(self, jsonData: str) -> SystemPerformanceData:
        try:
            data = json.loads(jsonData)
            spd = SystemPerformanceData()
            spd.setCpuUtil(data.get("cpuUtil", 0.0))
            spd.setMemoryUtil(data.get("memUtil", 0.0))
            spd.setTimeStamp(data.get("timeStamp", None))
            return spd
        except Exception as e:
            logging.error("Error parsing SystemPerformanceData JSON: %s", str(e))
            raise
