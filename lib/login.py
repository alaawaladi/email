import sys, os
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QLabel, QPushButton
from PySide2.QtCore import QFile, QIODevice, QObject


class LoginForm(QObject):
    
    def __init__(self, parent=None):
        super().__init__()
        self._loadLoginUi()
        
        self.login_label_message = self.login_window.findChild(QLabel, 'label_message')
        self.btn_login = self.login_window.findChild(QPushButton, 'LoginButton')

    def _loadLoginUi(self):
        ui_file = "%s/gui/GportalUI_login.ui"%os.getcwd()
        ui_file = QFile(ui_file)
        if not ui_file.open(QIODevice.ReadOnly):
            print("Cannot open login {}: {}".format(ui_file, ui_file.errorString()))
            sys.exit(-1)
        
        loader = QUiLoader()
        self.login_window = loader.load(ui_file, None)
        ui_file.close()
        if not self.login_window:
            print(loader.errorString())
            sys.exit(-1)
        
    def _setLoginErrorMessage(self, text):
        """ Set the display's error message """
        self.login_label_message.setText("")
        self.login_label_message.setText('<html><head/><body><p align="center"><span style=" font-size:8pt; color:#ff0000;">%s</span></p></body></html>'%text)
        self.login_label_message.adjustSize()
