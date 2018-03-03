# Andriy Kravchuk, 2018
# Union, SK,  Application Performance monitoring
#
import os, sys, configparser, time, random, uuid, datetime, threading
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities as DC
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


configuration = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
configuration.read("main.conf")

CLICK = 1
SEND_KEYS = 1
LOG_LEVEL = "debug"
TIMEOUT = 61
SCREENSHOTS_FOLDER = "screenshots"
LOG_FILENAME = configuration["browser"]["log_filename"]
#FIREFOX = r'FirefoxPortable\App\Firefox\firefox.exe'

class performanceTimer:
    def __call__(self, f):
        def wrapped_f(*args, **kwargs):
            before = datetime.datetime.now()
            f(*args, **kwargs)
            after = datetime.datetime.now()
            return round((after-before).total_seconds(), 1)
        return wrapped_f

class Browser(webdriver.Firefox):
    timeout = TIMEOUT
    #binary = FIREFOX
    HTTP_PROXY = configuration["browser"]["http_proxy"]
    HTTP_PROXY_PORT = configuration["browser"]["proxy_port"]
    NOPROXY = configuration["browser"]["no_proxy"].split(", ")

    def __init__(self, *args, **kwargs):
        # in case of Windows
        # self.set_capabilities()
        # binary = FirefoxBinary(self.binary)
        # webdriver.Firefox.__init__(
        #     self,
        #     firefox_binary=binary,
        #     capabilities=self.capabilities
        # )
        self.set_capabilities()
        self.set_proxy()
        super().__init__(*args, **kwargs, capabilities=self.capabilities)

        # binary = FirefoxBinary(self.binary)
        #self.set_capabilities()

    def set_capabilities(self):
        capabilities = DC.FIREFOX.copy()
        capabilities["moz:firefoxOptions"] = {
            "log":{
                "level": LOG_LEVEL
            }
        }
        self.capabilities = capabilities

    def set_proxy(self):
        proxy = Proxy()
        proxy.proxyType=ProxyType.MANUAL
        proxy.http_proxy = "%s:%s" % (self.HTTP_PROXY, self.HTTP_PROXY_PORT)
        proxy.no_proxy = self.NOPROXY
        proxy.add_to_capabilities(self.capabilities)

    def find_and_action(self, xpath, action, text=""):
        try:
            if action is SEND_KEYS:
                WebDriverWait(self, self.timeout).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                ).send_keys(text)
            if action is CLICK:
                WebDriverWait(self, self.timeout).until(
                    EC.element_to_be_clickable((By.XPATH, xpath))
                ).click()
        except:
            print("%s is not accessible" % xpath)
            self.screenShotMe()
            self.quit()
            sys.exit()

    @performanceTimer()
    def find(self, xpath):
        try:
            WebDriverWait(self, self.timeout).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
        except:
            print("%s isn't accessible" % xpath)
            self.screenShotMe()

    def deauthenticate(self):
        self.get(configuration["url"]["deauthenticate_url"])

    def screenShotMe(self):
        filename = "./%s/%s.png" % (SCREENSHOTS_FOLDER, str(uuid.uuid1()))
        self.save_screenshot(filename)

    def saveLog(self, performance):
        with open(LOG_FILENAME, "a") as f:
            f.write("%s\n" % performance)

def worker():
    me = Browser()
    # authenticate
    me.get(configuration["url"]["index_url"])
    me.find_and_action(
        configuration["page_elements"]["username_x"],
        SEND_KEYS,
        configuration["credentials"]["username"]
    )
    me.find_and_action(
        configuration["page_elements"]["password_x"],
        SEND_KEYS,
        configuration["credentials"]["password"]
    )
    me.find_and_action(
        configuration["page_elements"]["pin_x"],
        SEND_KEYS,
        configuration["credentials"]["pin"]
    )
    me.find_and_action(
        configuration["page_elements"]["login_x"],
        CLICK)

    me.get(configuration["url"]["podanie_davky_url"])

    me.find_and_action(
        configuration["page_elements"]["vytvor_davku_x"],
        CLICK)

    me.find_elements_by_xpath(
        configuration["page_elements"]["mesacny_vykaz_x"]
        )[1].click()

    # critical part which is under monitoring
    before = datetime.datetime.now()
    me.find_and_action(
        configuration["page_elements"]["pridaj_zamestnanca_x"],
        CLICK)
    me.find_and_action(
        configuration["page_elements"]["zrusit_btn_x"],
        CLICK)
    after = datetime.datetime.now()
    performance = round((after-before).total_seconds(), 1)
    print("performance = %s" % performance)

    me.deauthenticate()
    me.quit()
    me.saveLog(performance)

def main():
    thread1 = threading.Thread(target=worker)
    thread1.start()
    thread1.join()

if __name__ == "__main__":
    main()






























# pass
