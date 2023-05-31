import os, sys, time
import logging
from PyQt6.QtCore import pyqtSignal, QObject


class QTextEditLogger(logging.Handler):
    def __init__(self, widget):
        logging.Handler.__init__(self)
        self.widget = widget

    def emit(self, record):
        record = self.format(record)
        if record:
            time.sleep(0.2)
            XStream.stdout().messageWritten.connect(self.widget.append)
            XStream.stdout().write('%s' % record)
            XStream.stdout().messageWritten.disconnect()
            time.sleep(0.2)

class XStream(QObject):
    _stdout = None
    _stderr = None
    msgList = []
    messageWritten = pyqtSignal(str)

    def flush(self):
        pass

    def fileno(self):
        return -1

    def write(self, msg):
        try:
            if (not self.signalsBlocked()):
                message = msg.split(" - ")
                if message[1] == "INFO":
                    if str(message[-1]).__contains__('Message sent to'):
                        self.messageWritten.emit(msg)
                    elif str(message[-1]).__contains__('Start Process') or str(message[-1]).__contains__('Finished'):
                        if message[-1] not in self.msgList:
                            self.msgList.append(message[-1])
                            self.messageWritten.emit(f'{message[0]} - {message[1]} - {message[-1]}')
                    elif str(message[-1]).__contains__("Captcha"):
                        self.messageWritten.emit(msg)
                    elif f'{message[-2]} - {message[-1]}' not in self.msgList:
                        self.msgList.append(f'{message[-2]} - {message[-1]}')
                        self.messageWritten.emit(msg)
                if message[1] in ("WARNING", "ERROR"):
                    if str(message[-1]).__contains__("Stopped"):
                        if message[-1] not in self.msgList:
                            self.msgList.append(message[-1])
                            self.messageWritten.emit(f'{message[0]} - {message[1]} - {message[-1]}')
                    else:
                        self.messageWritten.emit(msg)
        except:pass

    @staticmethod
    def stdout():
        if (not XStream._stdout):
            XStream._stdout = XStream()
            sys.stdout = XStream._stdout
        return XStream._stdout

    @staticmethod
    def stderr():
        if (not XStream._stderr):
            XStream._stderr = XStream()
            sys.stderr = XStream._stderr
        return XStream._stderr
    
class LogFilter(logging.Filter):
        def __init__(self, profile):
            self.profile = profile
        
        def filter(self, record):
            record.profile = self.profile
            return True

# GportalUi Params
GPORTALUI_VERSION = "V2.3.9 © GPortal 2023"
LOG_PATH = "%s\logs"%(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
NEWSLETTERS_LOG = "%s/newsletters.log"%(LOG_PATH)
OUTLOOKCREATOR_LOG = "%s/outlookCreator.log"%(LOG_PATH)
RECOVERY_LOG = "%s/recoveryapps.log"%(LOG_PATH)
GMAIL_RECOVERY_LOG = "%s/GmailApps.log"%(LOG_PATH)
GMAIL_COMPOSER_LOG = "%s/GmailComposer.log"%(LOG_PATH)
SEARCH_EMAILS_LOG = "%s/SearchEmails.log"%(LOG_PATH)
YAHOO_RECOVERY_LOG = "%s/YahooApps.log"%(LOG_PATH)

# FireFox settings
FIREFOX_EXE = "%s\driver\geckodriver.exe"%(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FIREFOX_LOG = "%s\logs\geckodriver.log"%(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Chrome settings
CHROME_PATH = "%s\driver"%(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CHROME_LOG = "%s\logs\chromedriver.log"%(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))