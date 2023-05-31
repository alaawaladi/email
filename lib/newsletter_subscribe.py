import re, logging
import ipaddress, time
from settings.config import *
from lib.webdriver import WebDriver

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

class NewsLetterSubscribe (WebDriver):
    """ newsletter subscribe class """

    def __init__(self, kwargs):
        super().__init__()

        self.browser = kwargs.get("browser", None)
        self.hide_browser = kwargs.get("hide_browser", False)
        self.logger_window = kwargs.get("logger_window", None)
    
    def validate_line(self, line):
        params = line.split(',')
        if len(params)!=3: return False, line
        
        email = params[0].strip()
        ip = params[1].strip()
        port = params[2].strip()
        #...match email
        match_eml = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", email)
        if not match_eml: return False, "email -> %s"%email
        #...match ip
        try:
            ipaddress.IPv4Address(ip)
        except: return False , "ip -> (%s)"%ip 
        #...match port
        match_port = re.search(r"^\d{4}$", port)
        if not match_port: return False, "port -> (%s)"%port

        return True, {"email":email, "ip":ip, "port":port}
    
    def _contentinstitute(self, row):
        self.logger.info("Subscribe %s to contentinstitute newsletter..."%row["email"])
        self.setUpDriver(proxy=row["ip"], port=row["port"], is_hidden=self.hide_browser, browser=self.browser)

        if self.driver:
            try :
                self.logger.info('Open URL')
                self.driver.get("https://news.contentinstitute.com/subscriptions")
                
                self.logger.info("Insert %s Email "%row['email'])
                Email_input = self.driver.find_element(by=By.XPATH, value="//*[@id='fe503']")                
                Email_input.send_keys(row["email"])
                    
                Lab2 = self.driver.find_element(by=By.XPATH, value="//*[@id='fe523']")
                Lab2.send_keys(Keys.DOWN)
                    
                Lab3 = self.driver.find_element(by=By.XPATH, value="//*[@id='fe517']")
                Lab3.click()
                    
                time.sleep(1)
                self.logger.info('SUBMIT ... ')
                SUBMIT = self.driver.find_element(by=By.XPATH, value="//*[@id='fe511']")
                SUBMIT.click()

                self.logger.info("Subscribe %s to contentinstitute [DONE]"%row["email"])
                
                self.driver.close()
            except :
                    self.logger.info("Error : Subscribe %s to contentinstitute [incomplete]"%row['email'])
                    self.driver.close()  
    def _litmus(self, row):
        self.logger.info("Subscribe %s to litmus newsletter..."%row["email"])
        time.sleep(1)
        
        self.setUpDriver(proxy=row["ip"], port=row["port"], is_hidden=self.hide_browser, browser=self.browser)

        if self.driver:
            try :
                self.logger.info("Open URL ")
                self.driver.get("https://www.litmus.com/subscribe")
                time.sleep(1)

                Scrool = self.driver.find_element(by=By.XPATH, value="//*[@id='text-two-columns-block_618bf0606cc82']/div")
                self.driver.execute_script("arguments[0].scrollIntoView();",Scrool)
                
                self.logger.info("Insert %s Email "%row['email'])
                
                Insert_Email = self.driver.find_element(by=By.XPATH, value="//*[@id='Email']")
                Insert_Email.send_keys(row["email"])
                
                self.logger.info("Check Elements ... ")
                
                Check1 = self.driver.find_element(by=By.XPATH, value="//*[@id='Lblsubscribe_to_litmus_news']")
                Check1.click()
                
                Check2 = self.driver.find_element(by=By.XPATH, value="//*[@id='Lblsubscribe_to_litmus_weekly']")
                Check2.click()
                
                Check3 = self.driver.find_element(by=By.XPATH, value="//*[@id='subscribe_to_product_updates']")
                Check3.click()
                        
                Check4 = self.driver.find_element(by=By.XPATH, value="//*[@id='subscribe_to_Litmus_Live']")
                Check4.click()
                
                fin = self.driver.find_element(by=By.XPATH, value="//*[@id='subscribe_to_product_updates']")
                self.driver.execute_script("arguments[0].scrollIntoView();",fin)
                
                time.sleep(0.5)
                Check5 = self.driver.find_element(by=By.XPATH, value="//*[@id='subscribe_to_CMO_Newsletter']")
                Check5.click()
                
                
                Check6 = self.driver.find_element(by=By.XPATH, value="//*[@id='subscribe_to_Reports_and_Ebooks']")
                Check6.click()
                
                
                time.sleep(2)
                self.logger.info("SUBMIT ... ") 
                SUBMIT = self.driver.find_element(by=By.CSS_SELECTOR, value=".mktoButton")
                SUBMIT.click()
                
                self.logger.info("Subscribe %s to Litmus [DONE]"%row["email"])
                
                self.driver.close()
            except :
                    self.logger.info("Error : Subscribe %s to litmus [incomplete]"%row['email'])
                    self.driver.close() 

    def _hubspot(self, row):
        self.logger.info("Subscribe %s to hubspot newsletter..."%row["email"])
        time.sleep(1)
        
        self.setUpDriver(proxy=row["ip"], port=row["port"], is_hidden=self.hide_browser, browser=self.browser)

        if self.driver:
            try :
                self.logger.info("Open URL ... ")
                self.driver.get("https://blog.hubspot.com/subscriptions")
                
                self.logger.info("Insert : Email... %s "%row['email'])
                Email_input = self.driver.find_element(by=By.XPATH, value="//*[@id='email-address']")
                Email_input.send_keys(row['email'])
                        
                time.sleep(2)
                self.logger.info("Check Elements ... ")
                Lab1 = self.driver.find_element(by=By.XPATH, value="/html/body/div[4]/div[1]/div[2]/div/div/span/div/article/div[2]/div/section[2]/div/div/form/ul[1]/li[2]")
                Lab1.click()
                        
                Lab2 = self.driver.find_element(by=By.XPATH, value="/html/body/div[4]/div[1]/div[2]/div/div/span/div/article/div[2]/div/section[2]/div/div/form/ul[1]/li[4]")
                Lab2.click()
                        
                Lab3 = self.driver.find_element(by=By.XPATH, value="/html/body/div[4]/div[1]/div[2]/div/div/span/div/article/div[2]/div/section[2]/div/div/form/ul[1]/li[6]")
                Lab3.click()
                        
                Lab4 = self.driver.find_element(by=By.XPATH, value="/html/body/div[4]/div[1]/div[2]/div/div/span/div/article/div[2]/div/section[2]/div/div/form/ul[1]/li[8]")
                Lab4.click()
                
                self.logger.info("SUBMIT ... ") 
                SUBMIT = self.driver.find_element(by=By.XPATH, value="/html/body/div[4]/div[1]/div[2]/div/div/span/div/article/div[2]/div/section[2]/div/div/form/div/input")
                SUBMIT.click()
                
                self.logger.info("Subscribe %s to hubspot [DONE]"%row["email"])
                
                self.driver.close()
            except :
                    self.logger.warning("Error : Subscribe %s to hubspot [incomplete]"%row['email'])
                    self.driver.close()
                    
    def _skimm(self, row):
        self.logger.info("Subscribe %s to theskimm newsletter..."%row["email"])
        time.sleep(1)
        
        self.setUpDriver(proxy=row["ip"], port=row["port"], is_hidden=self.hide_browser, browser=self.browser)
        
        if self.driver:
            
            try :
                self.logger.info('Open URL ...')
                self.driver.get('https://www.theskimm.com/daily-skimm')
                time.sleep(1)
                
                self.logger.info("Insert %s Email "%row['email'])
                lab1 = self.driver.find_element(by=By.XPATH , value="//*[@id='ds-marketing-page']/div/div/div[2]/div/div/div/div[2]/form/label/input")
                lab1.send_keys(row['email'])
                time.sleep(0.5)
                self.logger.info('SUBMIT ...')
                lab2 = self.driver.find_element(by=By.XPATH, value="//*[@id='ds-marketing-page']/div/div/div[2]/div/div/div/div[2]/form/button")
                lab2.click()
                
                self.logger.info("Subscribe %s to theskimm [DONE]"%row["email"])
                self.driver.close()
            
            except :
                    self.logger.warning("Error : Subscribe %s to theskimm [incomplete]"%row['email'])
                    self.driver.close()  
        
    def _generalassemb(self, row):
        self.logger.info("Subscribe %s to generalassemb newsletter..."%row["email"])
        time.sleep(1)
        
        self.setUpDriver(proxy=row["ip"], port=row["port"], is_hidden=self.hide_browser, browser=self.browser)
        if self.driver:
            try : 
                self.logger.info(" Open URL : ")
                self.driver.get("https://generalassemb.ly/get/guest-post-newsletter")
                        
                time.sleep(2) 
                self.logger.info("Insert %s Email "%row['email'])
                Email_input = self.driver.find_element(by=By.XPATH, value="//*[@id='enter-now']/div/div/div[2]/div/form/div[1]/div[1]/input[1]")
                Email_input.send_keys(row['email'])
                
                self.logger.info("SUBMIT ... ") 
                SUBMIT = self.driver.find_element(by=By.XPATH, value="//*[@id='enter-now']/div/div/div[2]/div/form/div[1]/div[2]/input")
                SUBMIT.click()

                self.logger.info("Subscribe %s to Generalassemb [DONE]"%row["email"])
                self.driver.close()
            except :
                    self.logger.warning("Error : Subscribe %s to Generalassemb [incomplete]"%row['email'])
                    self.driver.close() 
                    
    def _thehustle(self, row):
        self.logger.info("Subscribe %s to thehustle newsletter..."%row["email"])
        time.sleep(1)
        
        self.setUpDriver(proxy=row["ip"], port=row["port"], is_hidden=self.hide_browser, browser=self.browser)
        if self.driver:
            try :
                self.logger.info(" Open URL ...")
                self.driver.get("https://thehustle.co/")
                time.sleep(1)
                try : #
                        self.logger.info("Accept Cookies ... ")
                        allow_cookie = self.driver.find_element(by=By.ID, value='wt-cli-accept-btn')
                        allow_cookie.click()
                except :
                        self.logger.info('Cookies Not Clicked')
                        
                self.logger.info("Insert %s Email "%row['email'])
                lib1 =self.driver.find_element(by=By.XPATH, value="//*[@id='homepage-hero']/div[1]/input[27]")
                lib1.send_keys(row['email'])
                
                self.logger.info('Submit ...')
                lib2 = self.driver.find_element(by=By.XPATH, value="//*[@id='homepage-hero']/div[1]/input[28]")
                lib2.click()
                
                self.logger.info("Subscribe %s to thehustle [DONE]"%row["email"])
                self.driver.close()
            except :
                        self.logger.warning("Error : Subscribe %s to thehustle [incomplete]"%row['email'])
                        self.driver.close()
    def _typography(self, row):
        self.logger.info("Subscribe %s to typography newsletter..."%row["email"])
        time.sleep(1)
        self.setUpDriver(proxy=row["ip"], port=row["port"], is_hidden=self.hide_browser, browser=self.browser)
        
        if self.driver :
            try :
                self.logger.info('Open URL...')
                self.driver.get('https://www.typography.com/subscribe?path=foot')
                time.sleep(5)
                try : #
                        self.logger.info("Accept Cookies ... ")
                        al_cookie = self.driver.find_element(by=By.XPATH, value="//*[@id='onetrust-accept-btn-handler']")
                        al_cookie.click()
                        self.driver.implicitly_wait(2)
                except :
                        self.logger.info('Cookies Not Clicked')
                        
                time.sleep(3)
                self.logger.info("Insert %s Email "%row['email'])
                lab1 =self.driver.find_element(by=By.XPATH, value="//*[@id='email_address']")
                lab1.send_keys(row['email'])
                
                self.logger.info('Submit ...')
                lab2 = self.driver.find_element(by=By.XPATH, value="//*[@id='root']/div/main/div/div/div/div/form/div[2]/button")
                lab2.click()
                
                self.logger.info("Subscribe %s to typography [DONE]"%row["email"])
                self.driver.close()
            except :
                    self.logger.warning("Error : Subscribe %s to typography [incomplete]"%row['email'])
                    self.driver.close() 
    def _buffer(self, row):
        self.logger.info("Subscribe %s to buffer newsletter..."%row["email"])
        time.sleep(1)
        self.setUpDriver(proxy=row["ip"], port=row["port"], is_hidden=self.hide_browser, browser=self.browser)
        if self.driver :
            try  :
                self.logger.info('Open URL ...')
                self.driver.get("https://buffer.com/newsletter")
                time.sleep(3)
                # try : #
                #         self.logger.info("Accept Cookies ... ")
                #         al_cookie = self.driver.find_element(by=By.XPATH, value="//*[@id='cky-btn-accept']")
                #         al_cookie.click()
                # except :
                #         self.logger.info('Cookies Not Clicked')
                    
                time.sleep(2) 
                self.logger.info("Clear Input ")
                set_email = self.driver.find_element(by=By.XPATH, value="//*[@id='email-input']")
                set_email.clear()
                
                self.logger.info("Insert %s Email "%row['email'])
                set_email.send_keys(row['email'])
                
                time.sleep(2)
                self.logger.info("Submit ...")
                sub_news = self.driver.find_element(by=By.CLASS_NAME, value='style__ButtonWrapper-sc-oh47eg-0')
                sub_news.click()
                
                self.logger.info("Subscribe %s to buffer [DONE]"%row["email"])
                self.driver.close()
            except :
                
                self.logger.warning("Error : Subscribe %s to buffer [incomplete]"%row['email'])
                self.driver.close() 
    def _atlasobscura(self, row):
        self.logger.info("Subscribe %s to atlasobscura newsletter..."%row["email"])
        time.sleep(1)
        self.setUpDriver(proxy=row["ip"], port=row["port"], is_hidden=self.hide_browser, browser=self.browser)
        if self.driver:
            try :
                self.logger.info("Open URL ... ")
                self.driver.get("https://www.atlasobscura.com/newsletters")
                
                time.sleep(5)
                try : #
                        self.logger.info("Accept Cookies ... ")
                        al_cookie = self.driver.find_element(by=By.XPATH, value="//*[@id='onetrust-accept-btn-handler']")
                        al_cookie.click()
                except :
                        self.logger.info("Cookies Not Clicked")
                    
                Scrool = self.driver.find_element(by=By.XPATH, value="//*[@id='page-content']/div/div[2]")
                self.driver.execute_script("arguments[0].scrollIntoView();",Scrool)
                
                self.logger.info("check elements ... ")
                time.sleep(3)
                check1 = self.driver.find_element(by=By.XPATH,value="/html/body/div[2]/div/div[2]/form/div[2]/div/div")
                check1.click()

                check2 = self.driver.find_element(by=By.XPATH,value="/html/body/div[2]/div/div[2]/form/div[3]/div/div")
                check2.click()

                check3 = self.driver.find_element(by=By.XPATH,value="/html/body/div[2]/div/div[2]/form/div[4]/div/div")
                check3.click()

                check4 = self.driver.find_element(by=By.XPATH,value="/html/body/div[2]/div/div[2]/form/div[5]/div/div")
                check4.click()
                
                Scrool = self.driver.find_element(by=By.XPATH, value="//*[@id='page-content']/div/footer")
                self.driver.execute_script("arguments[0].scrollIntoView();",Scrool)
                time.sleep(2)
                self.logger.info("Insert %s Email "%row['email'])
                set_email = self.driver.find_element(by=By.XPATH, value='/html/body/div[2]/div/div[2]/form/div[7]/div[1]/div/input')
                set_email.send_keys(row['email'])
                time.sleep(1)
                self.logger.info("Submit ...")
                sub_email = self.driver.find_element(by=By.CLASS_NAME, value="btn-default")
                sub_email.click()
                
                self.logger.info("Subscribe %s to atlasobscura [DONE]"%row["email"])
                self.driver.close()
                    
            except :     
                    self.logger.warning("Error : Subscribe %s to atlasobscura [incomplete]"%row['email'])
                    self.driver.close()   
       
    def runlogger(self):
        if not os.path.exists(LOG_PATH):
            os.makedirs(LOG_PATH)
        logTextBox = QTextEditLogger(self.logger_window)
        self.logger = logging.getLogger("newsletters")
        self.logger.setLevel(logging.INFO)
        handler = logging.FileHandler(NEWSLETTERS_LOG,'w')
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logTextBox.setFormatter(formatter)
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