import email
import re, logging
import ipaddress, time
from settings.config import *
from lib.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from datetime import datetime
from PySide2.QtCore import QObject, Signal

import traceback

class OutlookCreate (WebDriver, QObject):
    """ Create And Login class """
    insertNewRow = Signal(int)
    appendData = Signal(list)
    
    def __init__(self, kwargs, ):
        super().__init__()
        QObject.__init__(self)
        
        self.action = kwargs.get("action", None)
        self.browser = kwargs.get("browser", False)
        self.launguage_browser= kwargs.get("launguage_browser", None)
        self.Creatorloger = kwargs.get('Creatorloger',None)
        self.tableWidget = kwargs.get('tableWidget',None)
        self.port = 3128

    def set_Stop_Process(self, stopped):
        self.stop_process = stopped

    def get_Stop_Process(self):
        return self.stop_process
        
    def create_data(self, line):
        params = line.split(',')
        if len(params)!=7: return False, line
        email = params[0].strip()
        password = params[1].strip()
        ip = params[2].strip()
        fname = params[3].strip()
        lname = params[4].strip()
        country = params[5].strip()
        date = params[6].strip()
        
        #...match email
        match_eml = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", email)
        if not match_eml: return False, "email -> %s"%email
        #...match ip
        try:
            ipaddress.IPv4Address(ip)
        except: return False , "ip -> (%s)"%ip 
        return True, { "email":email, "password" :password, "ip":ip, "fname":fname, "lname":lname,"country":country, "date":date }
     
    def create_outlook (self,row,view,item) :
        while not(self.get_Stop_Process()):
            #table 
            x = view.rowCount()
            self.insertNewRow.emit(x+1)
            now = datetime.now()
            date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
            
            data = [
                [x, 0, date_time],
                [x, 1, row['email']],
                [x, 2, row['password']],
                [x, 3, row['ip']],
            ]
            self.appendData.emit(data)
            
            self.logger.info('*'*40+' Start Create Outlook  '+"*"*40)
            self.logger.info("Create account : %s"%row['email'])
            
            if self.get_Stop_Process():
                break
            self.setUpDriver(proxy=row["ip"], browser=self.browser,port=self.port,launguage_browser=self.launguage_browser)
            if self.driver :
                self.driver.maximize_window()
                try :
                    try:
                        if self.get_Stop_Process():
                            break
                        self.logger.info("Open URL")
                        self.driver.get('https://signup.live.com/?lic=1')
                        WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH, "//*[@id='MemberName']")))
                    except:
                        self.logger.error('Cannot open URL')
                        break
                    
                    try : 
                        email_create = self.driver.find_element(by=By.XPATH, value="//*[@id='MemberName']")
                        email_create.send_keys(row['email'])
                        self.logger.info("Insert Email %s"%row['email'])
                    except :
                        self.logger.error(f'Cannot insert email {row["email"]}')
                        break
                    
                    try:
                        if self.get_Stop_Process():
                            break
                        next_PassStep = WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH , "//*[@id='iSignupAction']")))
                        next_PassStep.click()
                        self.logger.info('Next ...')
                    except:
                        self.logger.error(f'Cannot click next {row["email"]}')
                        break
                    
                    try :  
                        if self.get_Stop_Process():
                            break
                        self.driver.find_element(by=By.XPATH, value="//*[@id='MemberNameError']")
                        self.logger.error('Email Address Used %s'%row['email'])
                        self.appendData.emit([[x, 4, 'Process Stopped'], [x, 5, 'Email Address Used']])
                        return self.driver.close()
                    except :
                        pass

                    try:
                        if self.get_Stop_Process():
                            break
                        set_pass = WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH , "//*[@id='PasswordInput']")))
                        set_pass.send_keys(row['password'])
                        self.logger.info("Set Password ... ")
                    except:
                        self.logger.error('Cannot set password')
                        break
                    
                    try :
                        if self.get_Stop_Process():
                            break
                        Un=self.driver.find_element(by=By.XPATH, value="//*[@id='iOptinEmail']")
                        Un.click()
                        self.logger.info("Uncheck commercial CheckBox")
                    except: pass

                    try:
                        click_Next = WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH, "//*[@id='iSignupAction']")))
                        click_Next.click()
                        self.logger.info('Click next Information Step... ')
                    except:
                        self.logger.error(f'Cannot find next button {row["email"]}')
                        break

                    try :
                        if self.get_Stop_Process():
                            break
                        check_err = self.driver.find_element(by=By.XPATH, value="//*[@id='PasswordError']")
                        self.appendData.emit([[x, 4, 'Process Stopped'], [x, 5, 'Password Incorrect']])
                        self.logger.error('Password Incorrect')
                        return self.driver.close()
                    except :
                        pass
                    
                    try:
                        if self.get_Stop_Process():
                            break
                        O_Fname = WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH , "//*[@id='FirstName']")))
                        O_Fname.send_keys(row['fname'])
                        self.logger.info('Insert First Name : %s'%row['fname'])
                    except:
                        self.logger.error('Cannot set first name')
                        break

                    try:
                        if self.get_Stop_Process():
                            break
                        O_Lname = WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH , "//*[@id='LastName']")))
                        O_Lname.send_keys(row['lname'])
                        self.logger.info('Insert Last Name : %s'%row['lname'])
                    except:
                        self.logger.error('Cannot set last name')
                        break
                    
                    try:
                        submit = WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH, "//*[@id='iSignupAction']")))
                        submit.click()
                        self.logger.info("Click Next... ")
                    except:
                        self.logger.error(f'Next button not found {row["email"]}')
                        break
                    
                    try :
                        if self.get_Stop_Process():
                            break
                        check_err = self.driver.find_element(by=By.XPATH, value="//*[@id='ProfileAccrualError']")
                        self.logger.error('Invalid First name')
                        self.appendData.emit([[x, 4, 'Process Stopped'], [x, 5, 'Invalid first name']])
                        return self.driver.close()
                    except :pass
                        
                    try :
                        if self.get_Stop_Process():
                            break
                        check_err = self.driver.find_element(by=By.XPATH, value="//*[@id='LastNameError']")
                        self.logger.error('Invalid Last Name')
                        self.appendData.emit([[x, 4, 'Process Stopped'], [x, 5, 'Invalid last name']])
                        return self.driver.close()
                    except : pass
                
                    bd = row['date']
                    
                    d = bd.split("-")
                
                    for i in range(len(d)) :
                        if d[i][0]=='0' :
                            d[i]=d[i][1]
                    
                    C_code="//*[@id='Country']/option[@value='%s']"%row['country']
                    O_m="//*[@id='BirthMonth']/option[@value='{}']".format(d[1])
                    O_d="//*[@id='BirthDay']/option[@value='{}']".format(d[0])
                    
                    
                    try : 
                        if self.get_Stop_Process():
                            break
                        O_Country = WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH , C_code)))
                        O_Country.click()
                        self.logger.info("Insert Country code ...")
                    except :
                        self.logger.error("Country Not Found")
                        self.appendData.emit([[x, 4, 'Process Stopped'], [x, 5, 'Invalid country code']])
                        return self.driver.close()
                    time.sleep(1)
                    
                    self.logger.info("Set BirthDate ... ")
                    try : 
                        if self.get_Stop_Process():
                            break
                        O_month=WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH, O_m)))
                        O_month.click()
                        self.logger.info("Insert month ... ")
                    except :
                        self.logger.error("BirthMonth Incorrect ...")
                        self.appendData.emit([[x, 4, 'Process Stopped'], [x, 5, 'BirthMonth Incorrect']])
                        return self.driver.close()
                    try : 
                        if self.get_Stop_Process():
                            break
                        O_Date = WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH, O_d)))
                        O_Date.click()
                        self.logger.info("Insert date ...")
                    except :
                        self.logger.error("Birthday Incorrect ...")
                        self.appendData.emit([[x, 4, 'Process Stopped'], [x, 5, 'Birthday Incorrect']])
                        return self.driver.close()
                    try :
                        if self.get_Stop_Process():
                            break
                        Y_date = WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH, "//*[@id='BirthYear']")))
                        Y_date.send_keys(d[2])
                        self.logger.info('Insert BirthYear ...')
                    except :
                        self.logger.error("BirthYear Incorrect ...")
                        self.appendData.emit([[x, 4, 'Process Stopped'], [x, 5, 'BirthYear Incorrect']])
                        return self.driver.close()
                    
                    try :
                        if self.get_Stop_Process():
                            break
                        check_err = self.driver.find_element(by=By.XPATH, value="//*[@id='BirthDateError']/div")
                        self.logger.error("Invalid BirthDate")
                        self.appendData.emit([[x, 4, 'Process Stopped'], [x, 5, 'Invalid BirthDate']])
                        return self.driver.close()
                    except :pass
                    
                    try:
                        if self.get_Stop_Process():
                            break
                        SUBMIT = self.driver.find_element(by=By.XPATH, value="//*[@id='iSignupAction']")
                        SUBMIT.click()
                        self.logger.info('Click Next ')
                    except:
                        self.logger.error(f'Cannot find next {row["email"]}')
                        break

                    try : 
                        if self.get_Stop_Process():
                            break
                        num = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, "/html/body/div[1]/div/div/div[2]/div/div[1]/div[3]/div/div[1]/div[5]/div/div/form/div[2]")))
                        msg_en = "Add security info"
                        msg_fr = "Ajouter des informations de sécurité"
                        if msg_en in num.text or msg_fr in num.text: 
                            self.logger.error('Phone number Required')
                            return self.driver.close() 
                    except : pass
                    
                    if self.get_Stop_Process():
                        break
                    if WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="hipEnforcementContainer"]'))) :
                        if self.get_Stop_Process():
                            break
                        self.logger.warning("Captcha Detected")
                        self.appendData.emit([[x, 4, 'Process Stopped'], [x, 5, 'Error Captcha detected']])

                        time.sleep(2)
                        try : 
                            if self.get_Stop_Process():
                                break
                            self.logger.info('Please click Next To continue ... [ %s ]'%row['email'])
                            
                            time.sleep(2)
                            
                            self.logger.info("Wait For Captcha To be Solved... in [ %s ]"%row['email'])
                            
                            WebDriverWait(self.driver,180).until(EC.invisibility_of_element_located((By.XPATH, '//*[@id="hipEnforcementContainer"]')))
                            
                            self.logger.info('Captcha Solved')

                            try : 
                                if self.get_Stop_Process():
                                    break
                                SUBMIT = WebDriverWait(self.driver, 15).until(EC.visibility_of_element_located((By.XPATH, "//*[@id='idBtn_Back'] | //*[@id='id__0']")))
                                SUBMIT.click()
                            except : pass

                            if self.get_Stop_Process():
                                break
                            self.logger.info('Check created Account in [ %s ]'%row['email'])
                            self.driver.get('https://outlook.live.com/owa/?nlp=1')
                            i = WebDriverWait(self.driver, 150).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="searchBoxId-Mail"]')))

                            if i : 
                                self.logger.info("created account succeeded in !!! [ %s ]"%row['email'])
                                self.appendData.emit([[x, 4, 'Success'], [x, 5, 'Successfuly created']])
                                self.logger.info('*'*40+" Ending Process "+"*"*40)
                                return self.driver.close()
                                
                        except  Exception as e :
                            self.logger.error(str(e))
                            self.logger.error('Error To solve captch in [ %s ]'%row['email'])
                            return self.driver.close()
                        time.sleep(5)
                    
                        
                    elif self.driver.title == "Microsoft account" or self.driver.title == "Compte Microsoft" or "Outlook" in self.driver.title :
                        self.appendData.emit([[x, 4, 'Process Success'], [x, 5, 'Account Created']])
                        self.logger.info("Success !!! %s"%row['email'])
                        self.logger.info('*'*40+" Ending Process "+"*"*40)
                    self.driver.close()
                    self.driver.quit()
                        
                except Exception as e :
                    e = str(e)
                    self.appendData.emit([[x, 4, 'Process Stopped', ]])
                    self.logger.error("Error : "+e+" %s"%row['email'])
                    self.logger.info('*'*40+" Ending Process "+"*"*40)
            break
        if self.get_Stop_Process():
            self.logger.warning('Stopped')
        
     
    def login_data(self,lines) :
        params = lines.split(',')
        if len(params)!= 7 and len(params) !=3: return False, lines
        
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
    
    
    def login_outlook(self,row,view,item) :
        while not(self.get_Stop_Process()):
            self.logger.info("*"*40+" login start"+"*"*40) 
            x = view.rowCount()
            view.setRowCount(x+1)
            now = datetime.now()
            
            date_time = now.strftime("%m/%d/%Y, %H:%M:%S")

            data = [
                [x, 0, date_time],
                [x, 1, row['email']],
                [x, 2, row['password']],
                [x, 3, row['ip']]
            ]
            self.appendData.emit(data)
            
            if self.get_Stop_Process():
                break
            self.setUpDriver(proxy=row["ip"], browser=self.browser,port=self.port,launguage_browser=self.launguage_browser)
            try :
                if self.driver:
                    try : 
                        if self.get_Stop_Process():
                            break
                        self.logger.info("Open URL ... %s"%row['email'])
                        self.driver.get('https://login.live.com/')
                        WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH, "//*[@id='i0116']")))
                    except :
                        self.logger.error('Failed to open URL')
                        self.appendData.emit([[x, 4, 'Connection Error'], [x, 5, 'Proxy Connection Error']])
                        return self.driver.close()
                    
                    try:
                        if self.get_Stop_Process():
                            break
                        i_email = self.driver.find_element(by=By.XPATH, value="//*[@id='i0116']")
                        i_email.send_keys(row['email'])
                        self.logger.info("Set Email .. %s"%row['email'])
                    except:
                        self.logger.error(f'Cannot set email {row["email"]}')
                        break
                    
                    try:
                        SUBMIT = WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH, "//*[@id='idSIButton9']")))
                        SUBMIT.click()
                        self.logger.info("Click Next ... %s"%row['email'])
                    except:
                        self.logger.error(f'Cannot find Next button {row["email"]}')
                        break
                    
                    try : 
                        if self.get_Stop_Process():
                            break
                        check_err = self.driver.find_element(by=By.XPATH, value="//*[@id='usernameError']")
                        self.logger.info("check if Username exists ... %s"%row['email'])
                        self.appendData.emit([[x, 4, 'Stop Process'], [x, 5, 'Email Address not found']])
                        self.logger.error("Email not found")
                        return self.driver.close()   
                    except :pass

                    try:
                        if self.get_Stop_Process():
                            break
                        Pass_input = WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH, "//*[@id='i0118']")))
                        Pass_input.send_keys(row['password'])
                        self.logger.info('Insertion password ... %s'%row['email'])
                    except:
                        self.logger.error(f'Cannot set password {row["email"]}')
                        break
                    
                    try:
                        if self.get_Stop_Process():
                            break
                        SUBMIT = WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH, "//*[@id='idSIButton9']")))
                        SUBMIT.click()
                        self.logger.info("Click Next ... ")
                    except:
                        self.logger.error(f'Cannot click next {row["email"]}')
                        break
                    time.sleep(2)
                    try :
                        if self.get_Stop_Process():
                            break
                        locked = self.driver.find_element(by=By.XPATH, value="/html/body/div[1]/div/div/div[2]/div/div[1]/div[2]/div/div[2]/div[2]/div/div/section/div/div[1]")
                        l = "Your account has been locked"
                        if l in locked.text :
                            self.logger.error('This account has been locked %s'%row['email'])
                            self.appendData.emit([[x, 4, 'Stopped'], [x, 5, 'Locked account']])
                            return self.driver.close()
                    except :pass
                    time.sleep(2)
                    try :
                        if self.get_Stop_Process():
                            break
                        P = self.driver.find_element(by=By.XPATH, value="//*[@id='iSelectProofTitle']")
                        p_msg = "Help us protect your account"
                        if p_msg in P.text :
                            self.logger.error('Account need verification  %s'%row['email'])
                            self.appendData.emit([[x, 4, 'Stopped'], [x, 5, 'Locked account']])
                            return self.driver.close()
                    except :
                        pass
                    
                    try :
                        if self.get_Stop_Process():
                            break
                        check_err = self.driver.find_element(by=By.XPATH, value="//*[@id='passwordError']")
                        self.logger.info('Check Password ')
                        self.appendData.emit([[x, 4, 'Stopped'], [x, 5, 'Password Incorrect']])
                        self.logger.error("Password Incorrect %s"%row['email'])  
                        return self.driver.close() 
                    except :
                        pass  
                    
                    try:
                        s = WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH, "//*[@id='idBtn_Back']")))
                        self.logger.info("Stay Login click  No ... %s"%row['email']) 
                        s.click()
                        time.sleep(2)
                        self.logger.info("Check if login succeeded ... %s"%row['email'])
                        self.driver.get("https://outlook.live.com/")
                        WebDriverWait(self.driver, 150).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="searchBoxId-Mail"]')))
                        if self.get_Stop_Process():
                            break
                        self.logger.info("login succeeded !!! %s"%row['email'])
                        self.appendData.emit([[x, 4, 'Success'], [x, 5, 'Login Succeeded']])
                        self.logger.info('*'*40+" Ending Process "+"*"*40)
                    except:
                        self.logger.error("login Failed !!! %s"%row['email'])
                        self.appendData.emit([[x, 4, 'Failed'], [x, 5, 'Login failed']])
                    self.driver.close()
                    self.driver.quit()
                        
            except Exception as e :
                e = str(e)
                self.appendData.emit([[x, 4, 'Process Stopped'],])
                self.logger.error("Error : "+e+" %s"%row['email'])
                self.logger.info('*'*40+" Ending Process "+"*"*40)
            break
        if self.get_Stop_Process():
            self.logger.warning('Stopped')
              
                       
    def runlogger(self):
        if not os.path.exists(LOG_PATH):
            os.makedirs(LOG_PATH)
        logTextBox = QTextEditLogger(self.Creatorloger)
        self.logger = logging.getLogger("outlookCreator")
        self.logger.setLevel(logging.INFO)
        handler = logging.FileHandler(OUTLOOKCREATOR_LOG,'w')
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logTextBox.setFormatter(formatter)
        if self.logger.hasHandlers() : self.logger.handlers.clear()
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