#####
# 
# This class is part of the Programming the Internet of Things
# project, and is available via the MIT License, which can be
# found in the LICENSE file at the top level of this repository.
# 
# Copyright (c) 2020 by Andrew D. King
# 

import logging
import unittest
from time import sleep
from io import StringIO

from programmingtheiot.cda.system.SystemPerformanceManager import SystemPerformanceManager
from programmingtheiot.common.DefaultDataMessageListener import DefaultDataMessageListener


class SystemPerformanceManagerTest(unittest.TestCase):
    """
    This test case class contains very basic unit tests for
    SystemPerformanceManager. It should not be considered complete,
    but serve as a starting point for the student implementing
    additional functionality within their Programming the IoT
    environment.
    
    NOTE: This test MAY require the sense_emu_gui to be running,
    depending on whether or not the 'enableEmulator' flag is
    True within the ConstraineDevice section of PiotConfig.props.
    If so, it must have access to the underlying libraries that
    support the pisense module. On Windows, one way to do
    this is by installing pisense and sense-emu within the
    Bash on Ubuntu on Windows environment and then execute this
    test case from the command line, as it will likely fail
    if run within an IDE in native Windows.
    """

    @classmethod
    def setUpClass(cls):
        logging.basicConfig(format='%(asctime)s:%(module)s:%(levelname)s:%(message)s', level=logging.DEBUG)
        logging.info("Testing SystemPerformanceManager class...")
        cls.spMgr = SystemPerformanceManager()
        cls.defaultMsgListener = DefaultDataMessageListener()
        cls.spMgr.setDataMessageListener(cls.defaultMsgListener)

    def setUp(self):
        # Crear un StringIO para capturar los logs
        self.log_stream = StringIO()
        log_handler = logging.StreamHandler(self.log_stream)
        logging.getLogger().addHandler(log_handler)

    def tearDown(self):
        # Limpiar los handlers de logs
        logging.getLogger().handlers.clear()

    def testStartAndStopManager(self):
        # Llamar a startManager y verificar los logs
        self.spMgr.startManager()
        
        # Dar tiempo para que los logs se generen (usar menos tiempo en un test real)
        sleep(2)
        
        # Verificar los logs de inicio
        log_contents = self.log_stream.getvalue()
        self.assertIn("Starting SystemPerformanceManager...", log_contents)
        
        # Llamar a stopManager
        self.spMgr.stopManager()
        
        # Dar tiempo para que se generen los logs de detención
        sleep(2)
        
        # Verificar los logs de detención
        log_contents = self.log_stream.getvalue()
        self.assertIn("Stopped SystemPerformanceManager.", log_contents)

if __name__ == "__main__":
    unittest.main()
