import sys, os
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QLabel, QPushButton
from PySide2.QtCore import QFile, QIODevice, QObject


class GenerateWindow(QObject):
    def __init__(self, parent=None):         
        super().__init__()
        self.emailsgeneratorUi()
        
    def emailsgeneratorUi(self):
        ui_file = "%s/gui/Dialog_emlgenerator.ui"%(os.getcwd())
        ui_file = QFile(ui_file)
        if not ui_file.open(QIODevice.ReadOnly):
            print("Cannot open main window {}: {}".format(ui_file, ui_file.errorString()))
            sys.exit(-1)
            
        loader = QUiLoader()
        self.generate_window = loader.load(ui_file, None)
        ui_file.close()
        if not self.generate_window:
            print(loader.errorString())
            sys.exit(-1)