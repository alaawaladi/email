import re, logging
import ipaddress, time
from settings.config import *
from lib.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, date, timedelta  
from PyQt6.QtCore import QObject, pyqtSignal
class Yahoo_Recovery (WebDriver, QObject):
    """ Yahoo Recovery """
    insertNewRow = pyqtSignal(int)
    appendData = pyqtSignal(list)
    def __init__(self, kwargs):
        super().__init__()
        QObject.__init__(self)
        self.browser = kwargs.get("browser", None)
        self.hide_browser = kwargs.get("hide_browser", False)
        self.logger_window = kwargs.get("logger_window", None)
        self.tableWidget = kwargs.get('tableWidget',None)
        self.launguage_browser= kwargs.get("launguage_browser", None)
        self.port = 3128
    def setStop_Recovery_Process(self, stopped):
        self.stopProcess = stopped

    def get_Stop_Recovery_Process(self):
        return self.stopProcess

    def R_yahoo_data(self,line) :
        params = line.split(',')
        if len(params) !=3: return False, line
        
        email = params[0].strip()
        password = params[1].strip()
        ip = params[2].strip()
        #...match email
        match_eml = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", email)
        if not match_eml: return False, "email -> %s"%email
        #...match ip
        try:
            ipaddress.IPv4Address(ip)
        except: return False , "ip -> (%s)"%ip 
        return True, { "email":email, "password" :password, "ip":ip}
    
    def _Yahoo_account(self,row,rowCount,item,start_apps,date_from,search_keyword, date_to):
        while not(self.get_Stop_Recovery_Process()):
            try:
                self.logger.info("Start Process")
                time.sleep(5)
                self.logger.info("Login Start")
                time.sleep(1)
                self.currentRowNumber = rowCount
                self.row = row
                self.email = row['email']
                self.password = row['password']
                self.item = item
                self.start_apps = start_apps
                self.search_keyword = search_keyword
                self.date_from = date_from
                self.date_to = date_to
                self.insertNewRow.emit(self.currentRowNumber+1)
                now = datetime.now()
                date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
                data = [
                    [self.currentRowNumber, 0, date_time],
                    [self.currentRowNumber, 1, self.email],
                    [self.currentRowNumber, 2, self.password],
                    [self.currentRowNumber, 3, row["ip"]],
                    [self.currentRowNumber, 6, search_keyword],
                ]
                self.appendData.emit(data)
                
                self.setUpDriver(proxy=row["ip"], browser=self.browser,port=self.port,is_hidden=self.hide_browser, launguage_browser=self.launguage_browser) 
                try :
                    try :
                        self.logger.info("Open URL ...")
                        if self.browser == "FireFox" and self.launguage_browser == "French":
                            self.driver.get("https://fr.mail.yahoo.com/")
                        else:
                            self.driver.get('https://mail.yahoo.com/')
                        try:
                            sign_in = WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH, "//*[@id='signin-main']/div[1]/a")))
                            sign_in.click()
                        except:pass
                    except :
                        self.logger.error(f'Failed to open URL {self.email}')
                        data = [
                            [self.currentRowNumber, 4, "Connection Error"],
                            [self.currentRowNumber, 5, "Proxy Connection Error"],
                        ]
                        self.appendData.emit(data)
                        return
                    if self.get_Stop_Recovery_Process():
                        break
                    wait = WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH, "//div[@id='login-landing']/strong")))
                    self.getLocation()
                except Exception as e :
                    if self.get_Stop_Recovery_Process():
                        break

                    data = [
                        [self.currentRowNumber, 4, "Process Stopped"],
                        [self.currentRowNumber, 5, "Error"],
                    ]
                    self.appendData.emit(data)
                    self.logger.error(f"Error : {str(e)} {self.email}")
                    self.logger.info("Ending Process")
                    return 
            except Exception as e:
                if self.get_Stop_Recovery_Process():
                    break
                self.logger.error(str(e))
                data = [
                    [self.currentRowNumber, 5, "Error"],
                    [self.currentRowNumber, 7, "Stopped"],
                ]
                self.appendData.emit(data)
            break
        if self.get_Stop_Recovery_Process():
            self.logger.warning("Stopped")
            self.appendData.emit([[self.currentRowNumber, 7, "Stopped"]])
        self.destroyDriver()
        
    def getLocation(self):
        while not(self.get_Stop_Recovery_Process()):
            try:
                unique = WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH, "//div[@id='login-landing']/strong | //div[@id='password-challenge']/strong | //*[@id='email-verify-challenge']/div[1]")))
                if unique.text.lower() in ("sign in", "sign in to yahoo mail", "se connecter à yahoo mail"):
                    self.setEmail()
                elif unique.text.lower() in ("enter password", "saisissez votre mot de passe"):
                    self.setPassword()
                elif unique.text.lower() in ("enter verification code", "saisissez le code de vérification"):
                    self.logger.error("Verification Required !")
            except Exception as e:
                if self.get_Stop_Recovery_Process():
                    break
                data = [
                    [self.currentRowNumber, 5, "Error"],
                    [self.currentRowNumber, 7, "Stopped"],
                ]
                self.appendData.emit(data)
                self.logger.error(str(e))
            break
    
    def setEmail(self):
        while not(self.get_Stop_Recovery_Process()):
            try:
                email_field = WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH, "//input[@id='login-username']")))
                email_field.click()
                email_field.send_keys(Keys.CONTROL + "a")
                email_field.send_keys(Keys.DELETE)
                email_field.send_keys(self.email)
                if self.get_Stop_Recovery_Process():
                    break
                self.logger.info("Set Email ...")
                time.sleep(1)
                email_field.send_keys(Keys.RETURN)
                self.logger.info("Click Next ...")
                time.sleep(2)
            except:
                self.logger.error(f"Couldn't Find Email Field ! {self.email}")
                break
            try:
                if self.get_Stop_Recovery_Process():
                    break
                verfiyReq = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//*[@id='email-verify-challenge']/div[1]")))
                if verfiyReq.text.lower().__contains__("enter verification code"):
                    self.logger.warning("Verification Required !")
            except:pass
            try:
                enterPass = self.driver.find_element(By.XPATH, "//div[@id='password-challenge']/strong")
                if enterPass.text.lower() in ("enter password", "saisissez votre mot de passe"):
                    self.setPassword()
            except:pass
            try:
                self.driver.find_element(By.XPATH, "//*[@id='username-error']")
                self.emailError()
            except:
                self.detectCaptcha()
            break
    
    def emailError(self):
        while not(self.get_Stop_Recovery_Process()):
            self.logger.info(f"Check Email ... {self.email}")
            time.sleep(1)
            data = [
                [self.currentRowNumber, 4, "Process Stopped"],
                [self.currentRowNumber, 5, "Email Not Found"],
            ]
            self.appendData.emit(data)
            self.logger.error(f"Email Not Found {self.email}")
            break
    
    def setPassword(self):
        while not(self.get_Stop_Recovery_Process()):
            try:
                try:
                    self.driver.find_element(By.XPATH, "//*[@id='password-challenge']/form/p")
                    self.passError()
                    break
                except:pass
                passwd_field =  WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH, "//input[@id='login-passwd']")))
                passwd_field.click()
                passwd_field.send_keys(Keys.CONTROL + "a")
                passwd_field.send_keys(Keys.DELETE)
                passwd_field.send_keys(self.password)
                if self.get_Stop_Recovery_Process():
                    break
                self.logger.info("Set Password ...")
                time.sleep(1)
                self.logger.info("Click Next ..")
                passwd_field.send_keys(Keys.RETURN)
                time.sleep(2)
                self.detectCaptcha()
            except:
                self.logger.error(f"Could't Find Password field ! {self.email}")
                break
            try:
                errorPass = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//div[@id='password-container']/p[@class='error-msg'] | //*[@data-test-folder-container='Inbox']")))
                if errorPass.get_attribute("data-test-folder-container") == "Inbox":
                    self.goToHomePage()
                else:
                    self.passError()
            except:
                self.verifyAccount()
            break

    def passError(self):
        while not(self.get_Stop_Recovery_Process()):
            self.logger.info(f"Check Password ... {self.email}")
            time.sleep(1)
            data = [
                [self.currentRowNumber, 4, "Process Stopped"],
                [self.currentRowNumber, 5, "Password Incorrect"],
            ]
            self.appendData.emit(data)
            self.logger.error(f"Password Incorrect {self.email}")
            break

    def detectCaptcha(self):
        while not(self.get_Stop_Recovery_Process()):
            try:
                WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//*[@id='recaptcha-form']")))
                if self.get_Stop_Recovery_Process():
                    break
                self.logger.warning(f"Captcha detected ! {self.email}")
                time.sleep(1)
                self.logger.info(f"Please Solve The Captcha To Continue ... {self.email}")
                try:
                    WebDriverWait(self.driver, 180).until(EC.visibility_of_element_located((By.XPATH, "//div[@id='password-challenge']/strong | //*[@id='email-verify-challenge']/div[1]")))
                    self.getLocation()
                except:
                    if self.get_Stop_Recovery_Process():
                        break
                    self.logger.error(f"Captcha Not Solved ! {self.email}")
                    data = [
                        [self.currentRowNumber, 4, "Process Stopped"],
                        [self.currentRowNumber, 5, "Captcha Detected !"]
                    ]
                    self.appendData.emit(data)
            except:pass
            break
    
    def verifyAccount(self):
        while not(self.get_Stop_Recovery_Process()):
            try:
                _ = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//*[@id='challenge-selector-challenge']/strong")))
                self.logger.error(f"Verification required {self.email}")
            except:
                self.wait1hour()
            break
    
    def wait1hour(self):
        while not(self.get_Stop_Recovery_Process()):
            try:
                _ = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//div[@id='wait-challenge']")))
                self.logger.error(f"Cannot Continue The Process. Wait 1 hour {self.email}")
            except:
                pass
            break
    
    def goToHomePage(self):
        while not(self.get_Stop_Recovery_Process()):
            try:
                self.logger.info("Check If Login Succeeded ...")
                time.sleep(1)
                wait = WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH, "//*[@data-test-folder-container='Inbox']")))
                if self.get_Stop_Recovery_Process():
                    break
                self.logger.info("Login Succeeded !")
                data = [
                    [self.currentRowNumber, 4, "Logged In"],
                    [self.currentRowNumber, 5, "Login Succeeded"],
                ]
                self.appendData.emit(data)
                time.sleep(1)
                self.checkBoxes()
            except:
                self.logger.error(f"Login Failed ! {self.email}")
                data = [
                    [self.currentRowNumber, 4, "Failed"],
                    [self.currentRowNumber, 5, "Login Failed !"],
                    [self.currentRowNumber, 7, "Stopped"],
                ]
                self.appendData.emit(data)
                time.sleep(1)
            break
    
    def checkBoxes(self):
        if "open_inbox" in self.start_apps  :
            self.yahoo_open_inbox(self.date_from, self.search_keyword, self.date_to)
            
        if "open_spam" in self.start_apps :
            self.Yahoo_open_spam()
            
        if "not_spam" in self.start_apps:
            self.Yahoo_Remove_spam()
    
    def yahoo_open_inbox(self, date_from, search_keyword, date_to) :
        while not(self.get_Stop_Recovery_Process()):
            time.sleep(2)
            try :
                self.logger.info('Start Open Inbox Process')
                time.sleep(1)
                try:
                    if self.get_Stop_Recovery_Process():
                        break
                    time.sleep(10)
                    advanced = WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.XPATH, "//*[@data-test-id='advanced-search-button-with-label']")))
                    self.logger.info("Click In Advanced Button")
                    advanced.click()
                    time.sleep(1)
                except:
                    self.logger.error(f"Error To Open Advanced! {self.email}")
                    break
                try:
                    if self.get_Stop_Recovery_Process():
                        break
                    _ = WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH, "//*[@data-test-id='advanced-search-pane']")))
                    drop_down_list = WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH, "//*[@data-test-id='folder-menu-drop-down']")))
                    self.logger.info("Click On Folder Options")
                    drop_down_list.click()
                    time.sleep(1)
                except:
                    self.logger.error(f"Error To Open Folder Options {self.email}")
                    break
                try:
                    if self.get_Stop_Recovery_Process():
                        break
                    inbox_folder = WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH, "//*[@data-test-id='2']")))
                    self.logger.info("Select Inbox Folder")
                    inbox_folder.click()
                    time.sleep(2)
                except:
                    self.logger.error(f"Error To Select Inbox Folder {self.email}")
                    break
                try:
                    if self.get_Stop_Recovery_Process():
                        break
                    search_button = WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.XPATH, "//*[@data-test-id='adv-search-search-btn']")))
                    search_button.click()
                    time.sleep(2)
                    search_field = WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='mail-search']/div/div/div[1]/ul/li[2]/div/div/input[1]")))
                    self.logger.info("Click In Search Input")
                    search_field.click()
                    time.sleep(1)
                except:
                    self.logger.error(f"Error To Click The Search Field {self.email}")
                    break
                try:
                    if self.get_Stop_Recovery_Process():
                        break
                    search_field.send_keys(Keys.CONTROL + "a")
                    search_field.send_keys(Keys.DELETE)
                    self.logger.info("Set Search Keyword")
                    if search_keyword != ".*":
                        search_field.send_keys(f'subject:{search_keyword} after:"{date_from}" before:"{date_to}"')
                    else:
                        search_field.send_keys(f'after:"{date_from}" before:"{date_to}"')
                    search_field.send_keys(Keys.RETURN)
                    time.sleep(5)
                except:
                    self.logger.error(f"Error To Set Search Keyword {self.email}")
                    break
                try:
                    if self.get_Stop_Recovery_Process():
                        break
                    nothing_found = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//*[@data-test-id='empty-list-message'] | //*[@id='mail-app-component']/div[2]/div/div[2]/div[1]/span | //*[@id='mail-app-component']/div[2]/div/span")))
                    self.logger.error(f"Nothing Found In Inbox {self.email}")
                    break
                except:pass
                
                try  :
                    time.sleep(2)
                    emails = len(self.driver.find_elements(by=By.XPATH, value="//div[@data-test-id='virtual-list']/ul/li"))
                    x = 2
                    self.logger.info('Start Open Emails (Inbox)')
                    while x <= emails:
                        if self.get_Stop_Recovery_Process():
                            break
                        time.sleep(2)
                        try:
                            date_header = self.driver.find_element(By.XPATH, f"//div[@data-test-id='virtual-list']/ul/li[{str(x)}]/div | //div[@data-test-id='virtual-list']/ul/li[{str(x)}]/div/a")
                            if date_header.get_attribute("data-test-id") == "time-chunk-separator" or "pencil-ad-messageList":
                                x += 1
                        except:pass
                        enter_email = self.driver.find_element(by=By.XPATH, value=f"//div[@data-test-id='virtual-list']/ul/li[{str(x)}]/a")
                        enter_email.click()
                        time.sleep(2)
                        back = self.driver.find_element(by=By.XPATH, value="//*[@id='mail-app-component']/div/div/div[1]/button")
                        back.click()
                        time.sleep(2)
                        x += 1
                    if self.get_Stop_Recovery_Process():
                        break
                    self.logger.info("Open Inbox Success")
                    time.sleep(1)
                except :
                    self.logger.error(f'Failed to start process {self.email}')
                    break
                    
            except Exception as e :
                self.logger.error(f"Error : {str(e)} {self.email}")
                data = [
                    [self.currentRowNumber, 5, "Error"],
                    [self.currentRowNumber, 7, "Stopped"],
                ]
                self.appendData.emit(data)
                self.logger.info("Ending Process")
            break
    
    def Yahoo_open_spam(self):
        while not(self.get_Stop_Recovery_Process()):
            time.sleep(2)
            try:
                self.logger.info('Start Open Spam Process')
                time.sleep(1)
                try:
                    if self.get_Stop_Recovery_Process():
                        break
                    spam_folder = WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH, "//*[@id='app']/div[2]/div/div[1]/nav/div/div[3]/div[1]/ul/li[7]")))
                    self.logger.info("Select Spam Folder")
                    spam_folder.click()
                    time.sleep(2)
                except:
                    self.logger.error(f"Error To Open Spam Folder {self.email}")
                    break
                try:
                    if self.get_Stop_Recovery_Process():
                        break
                    nothing_found = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//*[@data-test-id='empty-list-message'] | //*[@id='mail-app-component']/div[2]/div/div[2]/div[1]/span | //*[@id='mail-app-component']/div[2]/div/span")))
                    self.logger.error(f"Nothing Found In Spam {self.email}")
                    break
                except:pass
                try:
                    time.sleep(2)
                    emails = len(self.driver.find_elements(by=By.XPATH, value="//div[@data-test-id='virtual-list']/ul/li"))
                    x = 2
                    self.logger.info('Start Open Emails (Spam)')
                    while x <= emails:
                        if self.get_Stop_Recovery_Process():
                            break
                        time.sleep(2)
                        try:
                            date_header = self.driver.find_element(By.XPATH, f"//div[@data-test-id='virtual-list']/ul/li[{str(x)}]/div | //div[@data-test-id='virtual-list']/ul/li[{str(x)}]/div/a")
                            if date_header.get_attribute("data-test-id") == "time-chunk-separator" or "pencil-ad-messageList":
                                x += 1
                        except:pass
                        enter_email = self.driver.find_element(by=By.XPATH, value=f"//div[@data-test-id='virtual-list']/ul/li[{str(x)}]/a")
                        enter_email.click()
                        time.sleep(2)
                        back = self.driver.find_element(by=By.XPATH, value="//*[@id='mail-app-component']/div/div/div[1]/button")
                        back.click()
                        time.sleep(2)
                        x += 1
                    if self.get_Stop_Recovery_Process():
                        break
                    self.logger.info("Open Spam Success")
                    time.sleep(1)
                except:
                    self.logger.error(f'Failed to start process {self.email}')
                    break
                    
            except Exception as e :
                self.logger.error(f"Error : {str(e)} {self.email}")
                data = [
                    [self.currentRowNumber, 5, "Error"],
                    [self.currentRowNumber, 7, "Stopped"],
                ]
                self.appendData.emit(data)
                self.logger.info("Ending Process")
            break
      
    def Yahoo_Remove_spam(self):
        while not(self.get_Stop_Recovery_Process()):
            time.sleep(2)
            try:
                self.logger.info('Start Not Spam Process')
                time.sleep(1)
                try:
                    if self.get_Stop_Recovery_Process():
                        break
                    spam_folder = WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH, "//*[@id='app']/div[2]/div/div[1]/nav/div/div[3]/div[1]/ul/li[7]")))
                    self.logger.info("Select Spam Folder (Not Spam)")
                    spam_folder.click()
                    time.sleep(2)
                except:
                    self.logger.error(f"Error To Open Spam Folder {self.email}")
                    break
                try:
                    if self.get_Stop_Recovery_Process():
                        break
                    nothing_found = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//*[@data-test-id='empty-list-message'] | //*[@id='mail-app-component']/div[2]/div/div[2]/div[1]/span | //*[@id='mail-app-component']/div[2]/div/span")))
                    self.logger.error(f"Nothing Found In Spam {self.email}")
                    break
                except:pass
                try:
                    if self.get_Stop_Recovery_Process():
                        break
                    checkbox = WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH, "//*[@id='mail-app-component']/div/div/div/div[1]/div/div[1]/div/div/ul/li[1]/span/button")))
                    self.logger.info("Select All Emails From Spam")
                    checkbox.click()
                    time.sleep(2)
                except:
                    self.logger.error(f"Error To Select All Emails {self.email}")
                    break
                try:
                    if self.get_Stop_Recovery_Process():
                        break
                    move_to_button = WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH, "//*[@id='mail-app-component']/div/div/div/div[1]/div/div[2]/div/div[2]/span/button")))
                    self.logger.info("Start Moving Emails")
                    move_to_button.click()
                    time.sleep(2)
                except:
                    self.logger.error(f"Error To Start Moving Emails {self.email}")
                    break
                try:
                    if self.get_Stop_Recovery_Process():
                        break
                    select_inbox = WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH, "//*[@id='app']/div[7]/div/div[1]/div/div/ul[2]/div/ul[1]/li[1]")))
                    self.logger.info("Select Inbox Folder")
                    select_inbox.click()
                    time.sleep(3)
                except:
                    self.logger.error(f"Error To Select Inbox Folder {self.email}")
                    break
                try:
                    if self.get_Stop_Recovery_Process():
                        break
                    result = WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH, "//*[@data-test-id='empty-list-message'] | //*[@id='mail-app-component']/div[2]/div/div[2]/div[1]/span | //*[@id='mail-app-component']/div[2]/div/span")))
                    self.logger.info("Emails Moved From Spam To Inbox With Success")
                    break
                except:
                    self.logger.error(f"Error To Move Emails From Spam To Inbox {self.email}")
                    break
                    
            except Exception as e :
                self.logger.error(f"Error : {str(e)} {self.email}")
                data = [
                    [self.currentRowNumber, 5, "Error"],
                    [self.currentRowNumber, 7, "Stopped"],
                ]
                self.appendData.emit(data)
                self.logger.info("Ending Process")
            break

    def runlogger(self):
        if not os.path.exists(LOG_PATH):
            os.makedirs(LOG_PATH)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        logTextBox = QTextEditLogger(self.logger_window)
        self.logger = logging.getLogger("YahooApps")
        self.logger.setLevel(logging.INFO)
        logTextBox.setFormatter(formatter)
        handler = logging.FileHandler(YAHOO_RECOVERY_LOG,'w')
        handler.setLevel(logging.INFO)
        handler.setFormatter(formatter)
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