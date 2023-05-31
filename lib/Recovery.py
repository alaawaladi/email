import re, logging
import ipaddress, time
from settings.config import *
from lib.webdriver import WebDriver
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PyQt6.QtCore import QObject, pyqtSignal

NOTHING_FOUND_CHROME = '/html/body/div[2]/div/div[2]/div[2]/div[2]/div[1]/div/div/div[3]/div/div[3]/div[1]/div[2]/div/div/span[1] | /html/body/div[2]/div/div[2]/div[2]/div[2]/div[2]/div/div/div[1]/div/div[3]/div[1]/div[2]/div/div/span[1] | /html/body/div[2]/div/div[2]/div[2]/div[2]/div[2]/div/div/div[1]/div/div[3]/div[1]/div[2]/div/div/span[1] | /html/body/div[2]/div/div[2]/div[2]/div[2]/div[1]/div/div/div[1]/div/div[3]/div[1]/div[2]/div/div/span'
NOTHING_FOUND_FIREFOX = '/html/body/div[2]/div/div[2]/div[2]/div[1]/div/div/div[3]/div[2]/div/div[1]/div[2]/div/div/span[1] | /html/body/div[2]/div/div[2]/div[2]/div[1]/div/div/div[3]/div[2]/div/div[1]/div[2]/div/div/span'
NOTHING_FOUND_CHROME_OTHER = '/html/body/div[2]/div/div[2]/div[2]/div[2]/div[1]/div/div/div[3]/div/div[3]/div[1]/div[2]/div/div[2]/span[1] | /html/body/div[2]/div/div[2]/div[2]/div[2]/div[2]/div/div/div[1]/div/div[3]/div[1]/div[2]/div/div[2]/span[1] | /html/body/div[2]/div/div[2]/div[2]/div[2]/div[1]/div/div/div[1]/div/div[3]/div[1]/div[2]/div/div[2]/span[1] | /html/body/div[2]/div/div[2]/div[2]/div[2]/div[2]/div/div/div[1]/div/div[3]/div[1]/div[2]/div/div[2]/span[1]'
NOTHING_FOUND_FIREFOX_OTHER = '/html/body/div[2]/div/div[2]/div[2]/div[1]/div/div/div[3]/div[2]/div/div[1]/div[2]/div/div[2]/span[1]'
class Recovery_Apps (WebDriver, QObject):
    """ Recovery Apps class """
    insertNewRow = pyqtSignal(int)
    appendData = pyqtSignal(list)

    def __init__(self, kwargs):
        super().__init__()
        QObject.__init__(self)
        self.browser = kwargs.get("browser", None)
        self.hide_browser = kwargs.get("hide_browser", False)
        self.launguage_browser= kwargs.get("launguage_browser", None)
        self.logger_window = kwargs.get("logger_window", None)
        self.tableWidget = kwargs.get('tableWidget',None)
        self.port = 3128
    
    def getStop_Recovery_Process(self):
        return self.Stop_Recovery_Process

    def setStop_Recovery_Process(self, stopped):
        self.Stop_Recovery_Process = stopped

    def recovery_data(self,line) :
        params = line.split(',')
        if len(params) !=3: return False, line
        
        email = params[0].strip()
        password = params[1].strip()
        ip = params[2].strip()
        #...match email
        match_eml = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", email)
        if not match_eml: return False, f"email -> {email}"
        #...match ip
        try:
            ipaddress.IPv4Address(ip)
        except: return False , f"ip -> ({ip})" 
        return True, { "email":email, "password" :password, "ip":ip}
    

    def _outlook_acount(self,row,rowCount,item,start_apps,dr,r_c,to_date) :
        while not(self.getStop_Recovery_Process()):
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
                self.dr = dr
                self.r_c = r_c
                self.to_date = to_date
                self.insertNewRow.emit(self.currentRowNumber+1)
                now = datetime.now()
                date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
                data = [
                    [self.currentRowNumber, 0, date_time],
                    [self.currentRowNumber, 1, self.email],
                    [self.currentRowNumber, 2, self.password],
                    [self.currentRowNumber, 3, row["ip"]],
                    [self.currentRowNumber, 6, r_c],
                ]
                self.appendData.emit(data)
                
                self.setUpDriver(proxy=row["ip"], browser=self.browser,port=self.port,is_hidden=self.hide_browser,launguage_browser=self.launguage_browser)
                try :
                    time.sleep(2)
                    try :
                        self.logger.info("Open URL ...")
                        self.driver.get('https://login.live.com/')
                        time.sleep(1)
                    except :
                        self.logger.error(f'Failed to open URL {self.email}')
                        data = [
                            [self.currentRowNumber, 4, "Connection Error"],
                            [self.currentRowNumber, 5, "Proxy Connection Error"],
                            [self.currentRowNumber, 7, "Stopped"],
                        ]
                        self.appendData.emit(data)
                        return 
                    if self.getStop_Recovery_Process():
                        break
                    wait = WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH, "//input[@id='i0116']")))
                    self.getLocation()
                except Exception as e :
                    if self.getStop_Recovery_Process():
                        break
                    data = [
                        [self.currentRowNumber, 4, "Process Stopped"],
                        [self.currentRowNumber, 5, "Error"]
                    ]
                    self.appendData.emit(data)
                    self.logger.error(f"Error : {str(e)} {row['email']}")
                    self.logger.info("Ending Process")
                    return
            except Exception as e:
                if self.getStop_Recovery_Process():
                    break
                self.logger.error(str(e))
                data = [
                    [self.currentRowNumber, 5, "Error"],
                    [self.currentRowNumber, 7, "Stopped"],
                ]
                self.appendData.emit(data)
            break
        if self.getStop_Recovery_Process():
            self.logger.warning("Stopped")
            self.appendData.emit([[self.currentRowNumber, 7, "Stopped"]])
        time.sleep(1)
        self.destroyDriver()
    
    def getLocation(self):
        while not(self.getStop_Recovery_Process()):
            try:
                unique = WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH, "//div[@role='heading']")))
                if unique.text.lower() in ("sign in", "connexion"):
                    self.setEmail()
                elif unique.text.lower() in ("enter password", "entrez le mot de passe"):
                    self.setPassword()
                elif unique.text.lower() in ("stay signed in?", "rester connecté ?"):
                    self.clickNo()
                else:
                    self.logger.error("Login Failed !")
                    data = [
                        [self.currentRowNumber, 4, "Failed !"],
                        [self.currentRowNumber, 5, "Login Failed !"],
                    ]
                    self.appendData.emit(data)
            except Exception as e:
                if self.getStop_Recovery_Process():
                    break
                data = [
                    [self.currentRowNumber, 5, "Error"],
                    [self.currentRowNumber, 7, "Stopped"],
                ]
                self.appendData.emit(data)
                self.logger.error(str(e))
            break
    
    def setEmail(self):
        while not(self.getStop_Recovery_Process()):
            try:
                self.logger.info("Set Email ...")
                i_email = self.driver.find_element(by=By.XPATH, value="//*[@id='i0116']")
                i_email.send_keys(Keys.CONTROL + "a")
                i_email.send_keys(Keys.DELETE)
                i_email.send_keys(self.email)
                
                time.sleep(1)  
                self.logger.info("Click Next ...")
                i_email.send_keys(Keys.RETURN)
                # SUBMIT = self.driver.find_element(by=By.XPATH, value="//*[@id='idSIButton9']")
                # SUBMIT.click()
                time.sleep(3)
            except:
                self.logger.error(f"Error To Set Email ... {self.email}")
                break
            try:
                usernameError = self.driver.find_element(By.XPATH, "//div[@id='usernameError']")
                if usernameError.get_attribute("id").lower() == "usernameerror":
                    self.ErrorEmail()
            except:
                self.getLocation()
            break
    
    def ErrorEmail(self):
        while not(self.getStop_Recovery_Process()):
            self.logger.info(f"Check Email ...{self.email}")
            data = [
                [self.currentRowNumber, 4, "Login Failed"],
                [self.currentRowNumber, 5, "Email Address Not Found"],
                [self.currentRowNumber, 7, "Stopped"],
            ]
            self.appendData.emit(data)
            self.logger.error(f"Email not found {self.email}")
            break

    def setPassword(self):
        while not(self.getStop_Recovery_Process()):
            try:
                time.sleep(1)       
                self.logger.info("Set Password ...")
                Pass_input = self.driver.find_element(by=By.XPATH, value="//*[@id='i0118']")
                Pass_input.send_keys(Keys.CONTROL + "a")
                Pass_input.send_keys(Keys.DELETE)
                Pass_input.send_keys(self.password)
                
                time.sleep(1)
                self.logger.info("Click Next ...")
                Pass_input.send_keys(Keys.RETURN)
                # SUBMIT = self.driver.find_element(by=By.XPATH, value="//*[@id='idSIButton9']")
                # SUBMIT.click()
                time.sleep(3)
            except:
                self.logger.error(f"Error To Set Password ... {self.email}")
                break
            try:
                passwordError = self.driver.find_element(By.XPATH, "//div[@id='passwordError']")
                if passwordError.get_attribute("id").lower() == "passworderror":
                    self.ErrorPassword()
            except:
                self.getLocation()
            break
    
    def ErrorPassword(self):
        while not(self.getStop_Recovery_Process()):
            self.logger.info(f'Check Password ... {self.email}')
            data = [
                [self.currentRowNumber, 4, "Login Failed !"],
                [self.currentRowNumber, 5, "Password Incorrect"],
                [self.currentRowNumber, 7, "Stopped"],
            ]
            self.appendData.emit(data)
            self.logger.error(f"Password Incorrect {self.email}")
            break
    
    def clickNo(self):
        while not(self.getStop_Recovery_Process()):
            try:
                self.logger.info("Stay Signed In? Click No")
                s = self.driver.find_element(by=By.XPATH, value="//*[@id='idBtn_Back']")
                s.click()
                time.sleep(1)
                self.goToHomePage()
            except Exception as e:
                data = [
                    [self.currentRowNumber, 4, "Process Stopped"],
                    [self.currentRowNumber, 5, "Login Failed !"],
                    [self.currentRowNumber, 7, "Stopped"],
                ]
                self.appendData.emit(data)
                self.logger.error(str(e))
            break

    def goToHomePage(self):
        while not(self.getStop_Recovery_Process()):
            try:
                self.logger.info("Check if login succeeded ...")
                self.driver.get("https://outlook.live.com/")
                if self.browser == "Chrome":
                    wait = WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH, "//input[@id='topSearchInput']")))
                elif self.browser == "FireFox":
                    wait = WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH, "//div[@id='searchBoxId-Mail']/div[2]/div/input")))
                if self.driver.title == "Microsoft Office Home" or self.driver.title == "Microsoft Office Accueil"  or self.driver.title == "Microsoft account" or "Outlook" in self.driver.title :
                    self.logger.info("Login Succeeded !")
                    time.sleep(1)
                    data = [
                        [self.currentRowNumber, 4, "Logged In"],
                        [self.currentRowNumber, 5, "Login Succeeded"],
                    ]
                    self.appendData.emit(data)
                    self.checkBoxes(self.row, self.dr, self.r_c, self.to_date)
                else :
                    self.logger.error(f"Login Failed ! {self.email}")
                    data = [
                        [self.currentRowNumber, 4, "Failed"],
                        [self.currentRowNumber, 5, "Login Failed !"],
                        [self.currentRowNumber, 7, "Stopped"],
                    ]
                    self.appendData.emit(data)
                    break
                time.sleep(1)
            except Exception as e:
                data = [
                    [self.currentRowNumber, 5, "Error"],
                    [self.currentRowNumber, 7, "Stopped"],
                ]
                self.appendData.emit(data)
                self.logger.error(str(e))
            break
            
    def checkBoxes(self, row, dr, r_c, to_date):
        if "open_inbox" in self.start_apps:
            self.Recovery_open_inbox(row,dr,r_c,to_date)
                
        if "open_spam" in self.start_apps:
            self.Recovery_open_spam(row,dr,r_c,to_date)

        if "not_spam" in self.start_apps:
            self.Recovery_not_spam(row,dr,r_c,to_date)

        if "move_to_focused" in self.start_apps:
            self.Recovery_move_to_focused(row)
    
    def Recovery_open_inbox(self,row,dr,r_c,to_date):
        while not(self.getStop_Recovery_Process()):
            time.sleep(1)
            try :
                if self.getStop_Recovery_Process():
                    break
                self.logger.info('Start Open Inbox Process')
                self.driver.set_page_load_timeout(60)
            
                try :
                    if self.getStop_Recovery_Process():
                        break
                    search_input = WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH, "//div[@id='searchBoxId-Mail']"))) 
                except : 
                    self.logger.error(f'Search input Not open (Inbox) {self.email}')
                    break
                try : 
                    if self.getStop_Recovery_Process():
                        break
                    wait = WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH, "//a[@id='O365_AppName']")))
                    self.logger.info("Click In Search Input (Inbox)")
                    search_input.click()
                    time.sleep(1)
                    select_folder = WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.XPATH, "//div[@id='searchScopeButtonId']")))
                    self.logger.info("Open Select Folder Option (Inbox)")
                    time.sleep(1)
                    # select_folder.click()
                    
                except :
                    self.logger.error(f'Error to Open Folder Selector (Inbox) {self.email}')
                    break
            
                try :
                    if self.getStop_Recovery_Process():
                        break
                    select_folder.click()
                    i = WebDriverWait(self.driver, 80).until(EC.visibility_of_element_located((By.XPATH, "//button[@id='searchScopeButtonId-list1']")))
                    self.logger.info('Select inbox Folder') 
                    i.click()
                    time.sleep(2)
                    
                except :
                    self.logger.error(f'Error To locate inbox folder {self.email}')
                    break
                try :
                    if self.getStop_Recovery_Process():
                        break
                    self.logger.info("Set Search Keyword (Inbox)")
                    i_k = WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH, "/html/body/div[2]/div/div[1]/div/div[1]/div[2]/div/div/div/div/div[1]/div[2]/div/div/div/div/div[1]/div/div[2]/div/input[1]")))
                    i_k.click()
                    time.sleep(1)
                    i_k.send_keys(Keys.CONTROL + "a")
                    i_k.send_keys(Keys.DELETE)
                    time.sleep(1)
                    if r_c == ".*" :
                        i_k.send_keys(f"received:{dr}..{to_date}")
                    else :
                        i_k.send_keys(f"received:{dr}..{to_date} {r_c}")
                except : 
                    self.logger.error(f'Error to Set Search Keyword {self.email}')
                    break
                try :
                    if self.getStop_Recovery_Process():
                        break
                    self.logger.info('Start Searching (Inbox)')
                    i_k.send_keys(Keys.RETURN)
                    time.sleep(5)
                
                except :
                    self.logger.error(f'Error To Start Searching (Inbox) {self.email}')
                    break

                try :
                    if self.getStop_Recovery_Process():
                        break
                    error_key = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, f"//div/button/strong | {NOTHING_FOUND_CHROME} | {NOTHING_FOUND_FIREFOX}")))
                    self.logger.error(f"Nothing found in Inbox Check keyword and Date {self.email}")
                    break
                except:pass
            
                try :
                    if self.getStop_Recovery_Process():
                        break
                    self.logger.info('Open Inbox emails')
                    time.sleep(1)
                    i = WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH, "//div[@role='listbox']/div/div/div")))                  
                    els = len(self.driver.find_elements(by=By.XPATH, value="//div[@role='listbox']/div/div/div"))
                    i = 2
                    self.logger.info("Start Opening Emails (Inbox)")
                    self.driver.implicitly_wait(5)
                    while i <= els :
                        if self.getStop_Recovery_Process():
                            break
                        ss = self.driver.find_element(by=By.XPATH, value=f"//div[@role='listbox']/div/div/div[{str(i)}]")
                        ss.click()
                        time.sleep(2)
                        i += 1
                    if self.getStop_Recovery_Process():
                        break
                    self.logger.info("Open inbox Success")
                        
                except : 
                    self.logger.error(f"Error To Open Inbox Emails {self.email}")
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
                
    def Recovery_open_spam(self,row,dr,r_c,to_date):
        while not(self.getStop_Recovery_Process()):
            time.sleep(1)
            try :
                if self.getStop_Recovery_Process():
                    break
                self.logger.info('Start Open Spam Process')
                time.sleep(1)
                self.driver.set_page_load_timeout(60)            
                try :
                    if self.getStop_Recovery_Process():
                        break
                    serach_input = WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH, "//div[@id='searchBoxId-Mail']"))) 
                except : 
                    self.logger.error(f'Search input Not open (Spam) {self.email}')
                    break
                try : 
                    if self.getStop_Recovery_Process():
                        break
                    try:
                        wait = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Exit Search'] | //button[@aria-label='Quitter la recherche']")))
                        wait.click()
                    except:pass
                    wait = WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH, "//a[@id='O365_AppName']")))
                    self.logger.info("Click In Search Input (Spam)")
                    serach_input.click()
                    time.sleep(1)
                    select_folder = WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='searchScopeWrapperId']")))
                    self.logger.info("Open Select Folder Option (Spam)")
                    # select_folder.click()
                    
                except :
                    self.logger.error(f'Error to Open Folder Selector (Spam) {self.email}')
                    break
            
                try :
                    if self.getStop_Recovery_Process():
                        break
                    select_folder.click()
                    i = WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH, "//*[@id='searchScopeButtonId-list2']")))
                    self.logger.info('Select spam Folder') 
                    i.click()
                    time.sleep(2)
                    
                except :
                    self.logger.error(f'Error To locate spam folder {self.email}')
                    break
                try :
                    if self.getStop_Recovery_Process():
                        break
                    self.logger.info("Set Search Keyword (Spam)")
                    serach_input = WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH, "/html/body/div[2]/div/div[1]/div/div[1]/div[2]/div/div/div/div/div[1]/div[2]/div/div/div/div/div[1]/div/div[2]/div/input[1]")))
                    serach_input.click()
                    time.sleep(1)
                    serach_input.send_keys(Keys.CONTROL + "a")
                    serach_input.send_keys(Keys.DELETE)
                    time.sleep(1)
                    if r_c == ".*" :
                        serach_input.send_keys(f"received:{dr}..{to_date}")
                    else :
                        serach_input.send_keys(f"received:{dr}..{to_date} {r_c}")
                except : 
                    self.logger.error(f'Error to Set Search Keyword (Spam) {self.email}')
                    break
                try :
                    if self.getStop_Recovery_Process():
                        break
                    self.logger.info('Start Searching (Spam)')
                    serach_input.send_keys(Keys.RETURN)
                    time.sleep(5)
                
                except :
                    self.logger.error(f'Error To Start Searching (Spam) {self.email}')
                    break
                
                try :
                    if self.getStop_Recovery_Process():
                        break
                    error_key = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, f"//div/button/strong | {NOTHING_FOUND_CHROME} | {NOTHING_FOUND_FIREFOX}")))
                    self.logger.error(f"Nothing found in Spam Check keyword and Date {self.email}")
                    break
                except:pass
                try :
                    if self.getStop_Recovery_Process():
                        break
                    self.logger.info('Open Spam Emails')
                    time.sleep(1)
                    i = WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH, "//div[@role='listbox']/div/div/div")))
                    els = len(self.driver.find_elements(by=By.XPATH, value="//div[@role='listbox']/div/div/div")) 
                    i = 2
                    M_emails = els-1
                    self.logger.info("Start Opening Emails (Spam)")
                    while i <= els :
                        if self.getStop_Recovery_Process():
                            break
                        ss = WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH, f"//div[@role='listbox']/div/div/div[{str(i)}]")))
                        ss.click()
                        try:
                            displayContent = WebDriverWait(self.driver, 15).until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "conten")))
                            if displayContent.text in ("Show blocked content", "Afficher le contenu bloqué"):
                                displayContent.click()
                                time.sleep(5)
                        except:pass
                        i += 1
                    if self.getStop_Recovery_Process():
                        break
                    self.logger.info("Open spam Success")
                        
                except : 
                    self.logger.error(f"Error To Open Spam Emails {self.email}")
                    break
                
            except Exception as e :
                data = [
                    [self.currentRowNumber, 5, "Error"],
                    [self.currentRowNumber, 7, "Stopped"],
                ]
                self.appendData.emit(data)
                self.logger.error(f"Error : {str(e)} {self.email}")
                self.logger.info("Ending Process")
            break
        
    def Recovery_not_spam(self,row,dr,r_c,to_date):
        while not(self.getStop_Recovery_Process()):
            self.logger.info("Start Not Spam Process")
            time.sleep(1)
            try :
                try :
                    if self.getStop_Recovery_Process():
                        break
                    serach_input = WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH, "//*[@id='searchBoxId-Mail']")))
                except : 
                    self.logger.error(f"Search Input Not Open (Not Spam) {self.email}")
                    break
                try : 
                    if self.getStop_Recovery_Process():
                        break
                    try:
                        wait = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Exit Search'] | //button[@aria-label='Quitter la recherche']")))
                        wait.click()
                    except:pass
                    wait = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//a[@id='O365_AppName']")))
                    self.logger.info("Click In Search Input (Not Spam)")
                    serach_input.click()
                    time.sleep(1)
                    el = WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='searchScopeWrapperId']")))
                    self.logger.info("Open Select Folder Option (Not Spam)")
                    # el.click()
                except :
                    self.logger.error(f'Error to Open Folder Selector (Not Spam) {self.email}')
                    break
            
                try:
                    if self.getStop_Recovery_Process():
                        break
                    el.click()
                    spam = WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='searchScopeButtonId-list2']")))
                    self.logger.info('Select Spam Folder (Not Spam)')
                    spam.click()
                    time.sleep(2)
                    
                except :
                    self.logger.error(f'Error To locate Spam folder (Not Spam) {self.email}')
                    break
                try : 
                    if self.getStop_Recovery_Process():
                        break
                    self.logger.info("Set Search Keyword (Not Spam)")
                    i_k = WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH, "/html/body/div[2]/div/div[1]/div/div[1]/div[2]/div/div/div/div/div[1]/div[2]/div/div/div/div/div[1]/div/div[2]/div/input[1]")))
                    i_k.click()
                    time.sleep(1)
                    i_k.send_keys(Keys.CONTROL + "a")
                    i_k.send_keys(Keys.DELETE)
                    time.sleep(1)
                    if r_c == ".*" :
                        i_k.send_keys(f"received:{dr}..{to_date}")
                    else :
                        i_k.send_keys(f"received:{dr}..{to_date} {r_c}")
                        
                except : 
                    self.logger.error(f'Error to Set Search Keyword (Not Spam) {self.email}')
                    break
                
                try :
                    if self.getStop_Recovery_Process():
                        break
                    self.logger.info('Start Searching (Not Spam)')
                    i_k.send_keys(Keys.RETURN)
                    time.sleep(5)
                except :
                    self.logger.error(f'Error To Start Searching (Not Spam) {self.email}')
                    break

                try :
                    if self.getStop_Recovery_Process():
                        break
                    error_key = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, f"//div/button/strong | {NOTHING_FOUND_CHROME} | {NOTHING_FOUND_FIREFOX}")))
                    self.logger.error(f"Nothing found Check keyword and Date {self.email}")
                    break
                except:pass
                if self.browser == "FireFox": 
                    try : 
                        if self.getStop_Recovery_Process():
                            break
                        mx = WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH, "//div[@role='checkbox']")))
                        self.logger.info("Select All Emails in Spam Folder")
                        mx.click()
                        time.sleep(2)
                    except :
                        self.logger.error(f'Error To Select Junk Emails {self.email}')
                        break
                    try : 
                        if self.getStop_Recovery_Process():
                            break
                        self.logger.info("Start Moving Emails To Inbox")
                        time.sleep(1)
                        s = WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH, "//button[@name='Move to'] | //button[@name='Déplacer vers']")))
                        self.logger.info("Open Move Menu")
                        s.click()
                        time.sleep(2)
                    except :
                        self.logger.error(f"Error To Start Moving Emails To Inbox {self.email}")
                        break
                    try :
                        if self.getStop_Recovery_Process():
                            break
                        m = WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.XPATH, "//div[@role='menuitem'][@title='Boîte de réception'] | //div[@role='menuitem'][@title='Inbox']")))
                        m.click()
                        self.logger.info("Select Inbox Folder")
                        time.sleep(5)
                    except :
                        self.logger.error(f"Error To Select Inbox Folder In {self.email}")
                        break
                    try :
                        if self.getStop_Recovery_Process():
                            break
                        _ = WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH, NOTHING_FOUND_FIREFOX)))
                        self.logger.info("Emails Moved From Spam Folder Succeffuly")
                    except:
                        self.logger.error(f"Error To Move Emails (Not Spam) {self.email}")
                    break
                        
                #chrome driver
                else :
                    try : 
                        if self.getStop_Recovery_Process():
                            break
                        mx = WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH, "//div[@role='checkbox']")))
                        self.logger.info("Select All Emails In Spam Folder")
                        mx.click()
                        time.sleep(2)
                    except :
                        self.logger.error(f'Error To Select Junk Emails {self.email}')
                        break
                    try : 
                        if self.getStop_Recovery_Process():
                            break
                        self.logger.info("Start Moving Emails To Inbox")
                        time.sleep(1)
                        s = WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH, "//button[@aria-label='Move to'] | //button[@aria-label='Déplacer vers']")))
                        self.logger.info("Open Move Menu")
                        s.click()
                        time.sleep(2)
                    except :
                        self.logger.error(f"Error To Start Moving Emails To Inbox {self.email}")
                        break
                    try :
                        if self.getStop_Recovery_Process():
                            break
                        self.logger.info("Move Spam Emails To Inbox")
                        time.sleep(1)
                        sub = WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH, "//button[@name='Inbox'] | //button[@name='Boîte de réception']")))
                        self.logger.info("Click In Inbox Folder")
                        sub.click()
                        time.sleep(2)
                        
                        
                    except : 
                        self.logger.error(f"Failed To Move Emails From Spam To Inbox In {self.email}")
                        break
                    try :
                        if self.getStop_Recovery_Process():
                            break
                        confirm = WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH, "//*[@id='ok-1']")))
                        self.logger.info("Click OK In Alert Message")
                        confirm.click()
                        _ = WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH, NOTHING_FOUND_CHROME)))
                        self.logger.info("Move Emails From Spam Folder Success")
                    except :
                        self.logger.error(f"Error To Move Emails From Spam In {self.email}")
                        break
                    break
                    
            except Exception as e :
                self.logger.error(f"Error : {str(e)} {self.email}")
                data = [
                    [self.currentRowNumber, 5, "Error"],
                    [self.currentRowNumber, 7, "Stopped"]
                ]
                self.appendData.emit(data)
                self.logger.info("Ending Process")
            break
    
    def Recovery_move_to_focused(self, row):
        while not(self.getStop_Recovery_Process()):
            try:
                self.logger.info("Start Move To Focused Inbox")
                time.sleep(1)
                try:
                    if self.getStop_Recovery_Process():
                        break
                    try:
                        wait = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Exit Search'] | //button[@aria-label='Quitter la recherche']")))
                        wait.click()
                    except:pass
                    other_box = WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH, "//button[@name='Other'] | //button[@name='Autres']")))
                    self.logger.info("Select Other Box")
                    other_box.click()
                    time.sleep(2)
                except:
                    self.logger.error(f"Couldn't find 'Other Box' {self.email}")
                    break
                try:
                    if self.getStop_Recovery_Process():
                        break
                    nothing_found = WebDriverWait(self.driver, 15).until(EC.visibility_of_element_located((By.XPATH, f"{NOTHING_FOUND_CHROME_OTHER} | {NOTHING_FOUND_FIREFOX_OTHER}")))
                    self.logger.error(f"No Emails In Other Inbox {self.email}")
                    time.sleep(5)
                    break
                except:pass
                try : 
                    if self.getStop_Recovery_Process():
                        break
                    check_all = WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.XPATH, "//div[@role='checkbox']")))
                    self.logger.info("Select All Emails in Other Inbox")
                    check_all.click()
                    time.sleep(2)
                except :
                    self.logger.error(f'Error To Select Emails {self.email}')
                    break
                try : 
                    if self.getStop_Recovery_Process():
                        break
                    self.logger.info("Start Moving Emails To Focused Inbox")
                    time.sleep(1)
                    move_to = WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH, "//button[@aria-label='Move to'] | //button[@aria-label='Déplacer vers']")))
                    self.logger.info("Open Move To Menu")
                    move_to.click()
                    time.sleep(5)
                except :
                    self.logger.error(f"Error To Start Moving Emails {self.email}")
                    break
                try :
                    if self.getStop_Recovery_Process():
                        break
                    if self.browser == "Chrome":
                        focused_inbox = WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH, "//button[@name='Move to Focused inbox'] | //button[@name='Déplacer vers Prioritaire']")))
                    if self.browser == "FireFox":
                        focused_inbox = WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH, "//div[@role='menu']/div/ul[@role='presentation']/li[@role='presentation']/div/div[2]")))
                    self.logger.info("Select Focused Inbox")
                    focused_inbox.click()
                    time.sleep(5)
                except :
                    self.logger.error(f"Error To Select Focused Inbox {self.email}")
                    break
                try :
                    if self.getStop_Recovery_Process():
                        break
                    nothing_found = WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH, f"{NOTHING_FOUND_CHROME_OTHER} | {NOTHING_FOUND_FIREFOX_OTHER}")))
                    self.logger.info("Emails Moved From Other To Focused")
                except :
                    self.logger.error(f"Error To Move Emails From Other To Focused {self.email}")
                break
            except Exception as e:
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
        logTextBox = QTextEditLogger(self.logger_window)
        self.logger = logging.getLogger("recoveryapps")
        self.logger.setLevel(logging.INFO)
        handler = logging.FileHandler(RECOVERY_LOG,'w')
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