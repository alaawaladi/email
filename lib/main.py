import sys,os
from .login import LoginForm
from datetime import date
from .emailsgenerator import GenerateWindow
from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import QFile, QIODevice, Qt
from PySide2.QtWidgets import QDesktopWidget


class MainWindow(LoginForm,GenerateWindow):
    
    def __init__(self, parent=None):         
        super().__init__()
        self._loadMainWindowUi()

    def _loadMainWindowUi(self):
        ui_file = "%s/gui/GportalUI.ui"%(os.getcwd())
        ui_file = QFile(ui_file)
        if not ui_file.open(QIODevice.ReadOnly):
            print("Cannot open main window {}: {}".format(ui_file, ui_file.errorString()))
            sys.exit(-1)
            
        loader = QUiLoader()
        self.main_window = loader.load(ui_file, None)

        # Center window
        qRect = self.main_window.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qRect.moveCenter(centerPoint)
        self.main_window.move(qRect.topLeft())

        # set date_from, date_to to date of today
        ##Recovery
        self.main_window.dateEdit.setDate(date.today())
        self.main_window.dateTO.setDate(date.today())
        ##Search Emails
        self.main_window.dateEdit_From_Search.setDate(date.today())
        self.main_window.dateEdit_To_Search.setDate(date.today())
        ui_file.close()
        if not self.main_window:
            print(loader.errorString())
            sys.exit(-1)