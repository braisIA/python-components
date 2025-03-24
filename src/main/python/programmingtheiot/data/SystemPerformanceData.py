#####
# 
# This class is part of the Programming the Internet of Things project.
# 
# It is provided as a simple shell to guide the student and assist with
# implementation for the Programming the Internet of Things exercises,
# and designed to be modified by the student as needed.
#

import programmingtheiot.common.ConfigConst as ConfigConst
from programmingtheiot.data.BaseIotData import BaseIotData

class SystemPerformanceData(BaseIotData):
    """
    Representación de los datos de rendimiento del sistema,
    incluyendo la utilización de CPU y memoria.
    """

    def __init__(self, cpuUtil=None, memUtil=None, d=None):
        super(SystemPerformanceData, self).__init__(
            name=ConfigConst.SYS_PERF_NAME,
            typeID=ConfigConst.SYS_PERF_TYPE,
            d=d
        )

        self.cpuUtil = cpuUtil if cpuUtil is not None else ConfigConst.DEFAULT_VAL
        self.memUtil = memUtil if memUtil is not None else ConfigConst.DEFAULT_VAL

    def getCpuUtilization(self) -> float:
        return self.cpuUtil

    def getMemoryUtilization(self) -> float:
        return self.memUtil

    def setCpuUtilization(self, cpuUtil: float):
        self.cpuUtil = cpuUtil
        self.updateTimeStamp()

    def setMemoryUtilization(self, memUtil: float):
        self.memUtil = memUtil
        self.updateTimeStamp()

    def _handleUpdateData(self, data):
        if isinstance(data, SystemPerformanceData):
            self.cpuUtil = data.getCpuUtilization()
            self.memUtil = data.getMemoryUtilization()
        else:
            raise ValueError("Expected a SystemPerformanceData instance.")

    def __str__(self):
        return (
            f"SystemPerformanceData [ name = {self.name}, "
            f"CPU Utilization = {self.cpuUtil}%, "
            f"Memory Utilization = {self.memUtil}%, "
            f"timestamp = {self.timeStamp} ]"
        )
