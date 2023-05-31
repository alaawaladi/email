import subprocess
from sys import stdout
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FireFoxService
from selenium.webdriver.firefox.options import Options
from settings.config import *
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.service import Service as ChromeService
import chromedriver_autoinstaller 


class WebDriver:

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

    def setUpDriver(self, user_agent=None, is_hidden=False, browser='Firefox',launguage_browser='English', profile=None) :
        """ set up webdriver browser """ 
        profile_path = profile.replace(f'{profile.split("/")[-1]}', '')
        profile = profile.split("/")[-1]
        self.user_agent = user_agent 
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36" if self.user_agent is None else self.user_agent
            
        if launguage_browser == "French" :
            launguage_browser = "fr"
        if launguage_browser == "English" :
            launguage_browser = "en-GB"
            
        if browser == "Chrome":
            #...Chrome settings
            c = DesiredCapabilities.CHROME
            c["pageLoadStrategy"] = "none"

            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument("--headless")
            chrome_options.add_experimental_option("detach", True)
            chrome_options.add_argument("--start-maximized")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled") 
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"]) 
            chrome_options.add_experimental_option("useAutomationExtension", False)
            chrome_options.add_argument("--lang={}".format(launguage_browser)) 
            chrome_options.add_argument("--disable-notifications")
            #Adblock Extension  
            #chrome_options.add_extension("driver/extension_4_0_0_0.crx")
            chrome_options.headless = is_hidden
            chrome_options.add_argument(f"--user-data-dir={profile_path}")
            chrome_options.add_argument(f"--profile-directory={profile}")

            chrome_exe_path = chromedriver_autoinstaller.install(path=CHROME_PATH)

            chrome_service = ChromeService(executable_path=chrome_exe_path, log_path=CHROME_LOG)
            chrome_service.creationflags = subprocess.CREATE_NO_WINDOW
            self.driver = webdriver.Chrome(options=chrome_options, desired_capabilities=c, service=chrome_service)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.execute_cdp_cmd("Network.enable", {})
            self.driver.execute_cdp_cmd("Network.setExtraHTTPHeaders", {"headers": {"User-Agent": self.user_agent}})
            self.driver.execute_cdp_cmd("Network.setUserAgentOverride", {"userAgent": self.user_agent})
        else:
            #...Firefox settings
            self.firefox_options=Options()
            self.firefox_options.headless = is_hidden
            self.firefox_options.set_preference('intl.accept_languages', launguage_browser)
            self.firefox_options.set_preference('network.proxy.type', 1)
            self.firefox_options.set_preference("general.useragent.override", self.user_agent)
            self.firefox_options.set_preference("dom.push.enabled", False)
            firefox_service = FireFoxService(executable_path=FIREFOX_EXE, log_path=FIREFOX_LOG)
            firefox_service.creationflags=subprocess.CREATE_NO_WINDOW
            self.driver = webdriver.Firefox(options=self.firefox_options, service=firefox_service)

    def destroyDriver(self):
        try:
            self.driver.quit()
        except:
            pass