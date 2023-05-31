import sys, socket, re, subprocess, time
from sys import stdout
from selenium import webdriver
from settings.config import *
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import undetected_chromedriver as uc
import pyautogui

WIDTH, HEIGHT = pyautogui.size()

class WebDriver_Gmail:

    def __init__(self):
        self.GOOGLE = 'google-chrome'
        self.CHROMIUM = 'chromium'
        self.LINUX = "linux"
        self.MAC = "mac"
        self.WIN = "win"
        self.user_agent = None
        self.driver = None
        self.logger = None
        self.verified_proxy = []

    def checkProxy(self, ip, port):
        """ check proxy connectivity """ 
        try:
            self.logger.info("Check proxy")
            time.sleep(1)
            s = socket.socket()
            s.settimeout(10)

            proxy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                proxy.connect((ip, int(port)))
            except Exception as e:
                self.logger.error('Proxy not OK: [%s]'%(ip))
                return False
            self.logger.info('Proxy Is OK: [%s]'%ip)
            return True
        except Exception as e:
            self.logger.error(str(e))

    def os_name(self):
        pl = sys.platform
        if pl == "linux" or pl == "linux2": return self.LINUX
        elif pl == "darwin": return self.MAC
        elif pl == "win32": return self.WIN

    def chrome_version(self, browser_type=None):

        browser_type = self.GOOGLE if not browser_type else browser_type

        pattern = r'\d+\.\d+\.\d+'
        cmd_mapping = {
            self.GOOGLE: {
                self.LINUX: 'google-chrome --version',
                self.MAC: r'/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --version',
                self.WIN: r'reg query "HKEY_CURRENT_USER\Software\Google\Chrome\BLBeacon" /v version'
            },   
            self.CHROMIUM: {
                self.LINUX: 'chromium --version',
                self.MAC: r'/Applications/Chromium.app/Contents/MacOS/Chromium --version',
                self.WIN: r'reg query "HKEY_CURRENT_USER\Software\Chromium\BLBeacon" /v version'
            }
        }
        
        cmd = cmd_mapping[browser_type][self.os_name()]
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        process = subprocess.Popen(cmd, startupinfo=startupinfo, stdout= subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        stdout = process.stdout.read().decode('utf8')
        version = re.search(pattern, stdout)
        if version:
            return version.group(0).split('.')[0]
        
        return False

    def setUpDriver(self, user_agent=None, proxy=None, port=3128, is_hidden=False, browser='Chrome',launguage_browser='English') :
        """ set up webdriver browser """ 
        try:
            self.user_agent = user_agent 
            self.user_agent = "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:63.0) Gecko/20100101 Firefox/63.0"  if self.user_agent is None else self.user_agent
            #...Porxy connection
            if proxy not in self.verified_proxy:
                proxy_status = self.checkProxy(proxy, port)
                if not proxy_status: return False
                self.verified_proxy.append(proxy)
                
            if launguage_browser == "French" :
                launguage_browser = "fr"
            if launguage_browser == "English" :
                launguage_browser = "en-GB"
                
            if browser == "Chrome":
                #...Chrome settings
                c = DesiredCapabilities.CHROME
                c["pageLoadStrategy"] = "none"
                is_supported = False
                chrome_current_version = self.chrome_version()
                if chrome_current_version:
                    chrome_exe_path ="%s/chromedriver_%s.exe"%(CHROME_PATH, chrome_current_version)    
                    if os.path.exists(chrome_exe_path):
                        is_supported = True
                
                if not is_supported:
                    tmp_msg_err = "Chrome version used is not supported by application. Supported versions [>=105 and <=112]!"
                    self.logger.error(tmp_msg_err)
                    return False

                chrome_options = uc.ChromeOptions()
                if proxy: chrome_options.add_argument('--proxy-server=http://%s:%s'%(proxy, port))
                #chrome_options.add_argument("--start-maximized")
                chrome_options.add_argument("--lang={}".format(launguage_browser)) 
                #Adblock Extension  
                #chrome_options.add_extension("driver/extension_4_0_0_0.crx")
                chrome_options.headless = is_hidden
                self.driver = uc.Chrome(driver_executable_path=chrome_exe_path, desired_capabilities=c, options=chrome_options, service_creationflags=subprocess.CREATE_NO_WINDOW)
                self.driver.set_window_size((WIDTH/2), (HEIGHT/2))
                self.driver.set_window_position(0, 0)
                self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                    "source": """
                        Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                        })
                    """
                })
                self.driver.execute_cdp_cmd("Network.enable", {})
                self.driver.execute_cdp_cmd("Network.setExtraHTTPHeaders", {"headers": {"User-Agent": self.user_agent}})
        except Exception as e:
            self.logger.error(str(e))

    def destroyDriver(self):
        try:
            self.driver.delete_all_cookies()
            self.driver.close()
        except:
            pass

from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service

class WebDriver_Gmail_Composer:

    def __init__(self):
        self.driver = None
        self.logger = None
        self.user_agent = None

    def setUpDriver(self, user_agent=None, is_hidden=False, launguage_browser='English', profile=None) :
        """ set up webdriver browser """ 
        
        self.user_agent = user_agent 
        self.user_agent = "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:63.0) Gecko/20100101 Firefox/63.0"  if self.user_agent is None else self.user_agent
            
        if launguage_browser == "French" :
            launguage_browser = "fr"
        if launguage_browser == "English" :
            launguage_browser = "en-GB"

        # FireFox Options
        firefox_options = Options()
        firefox_options.headless = is_hidden
        firefox_options.binary = r'C:\Program Files\Mozilla Firefox\firefox.exe'
        firefox_options.profile = profile
        firefox_options.set_preference('intel.accept_languages', launguage_browser)
        firefox_options.set_preference('general.useragent.override', self.user_agent)
        firefox_options.set_preference('dom.webnotifications.enabled', False)
        firefox_options.set_preference('dom.push.enabled', False)

        # FireFox Services
        firefox_services = Service(executable_path=FIREFOX_EXE, log_path=FIREFOX_LOG)
        firefox_services.creationflags = subprocess.CREATE_NO_WINDOW

        self.driver = webdriver.Firefox(service=firefox_services, options=firefox_options)

    def destroyDriver(self):
        self.driver.quit()