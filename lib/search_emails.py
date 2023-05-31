from urllib import request, error
import imapclient, email, logging, imaplib, json, time
from settings.config import *

class Search_Emails:

    def __init__(self, logger, view):
        self._view = view
        self.logger_window = logger
        self._stopProcess = False
        self.numberItems = 0
    
    def setStopProcess(self, stopped):
        self._stopProcess = stopped
    
    def getStopProcess(self):
        return self._stopProcess
    
    def getServerSettings(self, addressMail):
        try:
            self.logger.info(f"Getting domain settings of {addressMail}...")
            time.sleep(1)
            website = request.urlopen(f"https://emailsettings.firetrust.com/settings?q={addressMail}")

            data = json.load(website)
            self._domain = data["domain"]
            settings = data["settings"]
            for i in settings:
                if i["protocol"].lower() == "imap":
                    host = i["address"]
                    break
            return host
        except error.HTTPError:
            self.logger.error("The Domain Incorrect Or Not Exist")
            self.setStopProcess(True)
    def getFolderName(self, imap, folderName):
        folders = imap.list_folders()
        folder = {}
        for i in range(len(folders)):
            for j in range(len(folders[i][0])):
                if folders[i][0][j].decode("utf-8") in ("\\HasNoChildren", "\\HasChildren"):
                    continue
                folder[folders[i][0][j].decode("utf-8")] = folders[i][2]
        return folder[f"\\{folderName}"]

    def search(self, email_address, password, date_from, date_to, subject, result, box):
        while not(self.getStopProcess()):
            try:
                if self.getStopProcess():
                    self.logger.warning("Stopped")
                    time.sleep(1)
                    break
                imap_server = self.getServerSettings(email_address)
                if self.getStopProcess():
                    self.logger.warning("Stopped")
                    time.sleep(1)
                    break
                self.logger.info(f"Connecting ... {email_address}")
                time.sleep(1)
                imap = imapclient.IMAPClient(host=imap_server, ssl=True)
                imap.login(username=email_address, password=password)
                if box == "Inbox":
                    imap.select_folder(box, readonly=True)
                else:
                    folder_name = self.getFolderName(imap, box)
                    imap.select_folder(folder_name, readonly=True)
                if self.getStopProcess():
                    self.logger.warning("Stopped")
                    time.sleep(1)
                    break
                if self._domain == "gmail.com":
                    if box=="Junk":
                        if subject == ".*":
                            self.msgsNumbers = imap.gmail_search(f"in:spam after:{date_from} before:{date_to}")
                        else:
                            self.msgsNumbers = imap.gmail_search(f"in:spam subject:{subject} after:{date_from} before:{date_to}")
                    else:
                        if subject == ".*":
                            self.msgsNumbers = imap.gmail_search(f"in:inbox after:{date_from} before:{date_to}")
                        else:
                            self.msgsNumbers = imap.gmail_search(f"in:inbox subject:{subject} after:{date_from} before:{date_to}")
                else:
                    if subject == ".*":
                        self.msgsNumbers = imap.search(['SINCE', date_from, 'BEFORE', date_to])
                    else:
                        self.msgsNumbers = imap.search(['SUBJECT', subject, 'SINCE', date_from, 'BEFORE', date_to])
                self.logger.info(f"Loading ... {len(self.msgsNumbers)} email(s)")
                time.sleep(1)
                if len(self.msgsNumbers) == 0:
                    break
                ###
                ResultList = []
                results = {}
                for _, msgData in imap.fetch(self.msgsNumbers, "RFC822").items():
                    if self.getStopProcess():
                        self.logger.warning("Stopped")
                        time.sleep(1)
                        break
                    emailMsg = email.message_from_bytes(msgData[b"RFC822"])
                    for key in result:
                        if self.getStopProcess():
                            self.logger.warning("Stopped")
                            time.sleep(1)
                            break
                        results[key] = emailMsg.get(key)
                    ResultList.append(results.copy())
                self.numberItems = len(ResultList)
                self._view.displayResult(ResultList)
            except imaplib.IMAP4.error as e:
                self.logger.error(str(e))
                self.setStopProcess(True)
                break
            except UnicodeEncodeError:
                self.logger.error(f"Check {email_address} password")
                self.setStopProcess(True)
                break
            except IndexError:
                self.logger.error("Remove Empty Lines")
                self.setStopProcess(True)
                break
            except Exception:
                self.logger.exception("Error")
                self.setStopProcess(True)
                break
            imap.logout()
            break
    
    def runlogger(self):
        if not os.path.exists(LOG_PATH):
            os.makedirs(LOG_PATH)
        logTextBox = QTextEditLogger(self.logger_window)
        self.logger = logging.getLogger("Search_Emails")
        self.logger.setLevel(logging.INFO)
        handler = logging.FileHandler(SEARCH_EMAILS_LOG,'w')
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logTextBox.setFormatter(formatter)
        if self.logger.hasHandlers():
            self.logger.handlers.clear()
        self.logger.addHandler(handler)
        self.logger.addHandler(logTextBox)
                
    def closeLogger(self):
        try:
            handlers = self.logger.handlers[:]
            for handler in handlers:
                handler.close()
                self.logger.removeHandler(handler) 
        except:
            pass

    def __del__(self):
        # close open logger
        self.closeLogger()