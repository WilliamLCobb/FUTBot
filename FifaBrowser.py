import time
import pyautogui
import platform

import random
import pickle

from config import *

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from browsermobproxy import Server



class FifaBrowser(object):
    def __init__(self):
        # Create Proxy
        self.server = Server(root_path+"/selenium/browsermob-proxy", {'port':8080})
        self.server.start()
        self.proxy = self.server.create_proxy()

        options = webdriver.ChromeOptions()
        options.add_argument('--proxy-server={host}:{port}'.format(host='localhost', port=self.proxy.port))
        if platform.system() == 'Windows':
            self.browser = webdriver.Chrome(root_path+'/selenium/chromedriver', chrome_options=options)
            self.input_controller = HIDInput_Windows(correction=(0, 0))
        else:
            self.browser = webdriver.Chrome(root_path+'/selenium/chromedriver-osx', chrome_options=options)
            self.input_controller = HIDInput_OSX(correction=(0, 5))

        self.browser.set_window_size(1440, 900)
        self.browser.set_window_position(0, 0)


        if (not self.input_controller.set_window("data:, - Google Chrome")):
            raise Exception

        time.sleep(5)
        print "Sending"

        # Member Variables
        self.cookiesLoaded = False


    def pause(self, lo, hi):
        k = 1000
        sleeptime = random.randint(lo * k, hi * k) / float(k)
        time.sleep(sleeptime)

    def save_cookies(self):
        pickle.dump( self.browser.get_cookies() , open(root_path+"/cookies.pkl","wb"))

    def load_cookies(self):
        if self.cookiesLoaded:
            return
        self.cookiesLoaded = True
        if os.path.isfile(root_path+"/cookies.pkl"):
            cookies = pickle.load(open(root_path+"/cookies.pkl", "rb"))
            for cookie in cookies:
                try:
                    self.browser.add_cookie(cookie)
                    print cookie
                except:
                    pass

    def clear_cookies(self):
        self.browser.delete_all_cookies()
        if os.path.isfile(root_path + "/cookies.pkl"):
            os.remove(root_path+"/cookies.pkl")

    # Interacting with main interface

    def search(self,  reauth=True, min_price = None, max_price = None, min_buy = None, max_buy = None, quality = None, id = 0):
        pass

    def buy_card(self, index):
        pass

    def sell_card(self):
        pass


    def login(self, email, password, answer):
        print "Logging in"
        self.browser.get("https://www.easports.com")

        self.load_cookies()

        self.browser.get("https://www.easports.com/fifa/ultimate-team/web-app")

        if self.browser.title == "Log In":
            self.clear_cookies()
            self.pause(3, 5)
            self.browser.get("https://www.easports.com/fifa/ultimate-team/web-app")
            self.browser.find_element_by_id("email").clear()
            self.browser.find_element_by_id("email").send_keys(email)
            self.browser.find_element_by_id("password").clear()
            self.browser.find_element_by_id("password").send_keys(password)
            self.pause(4, 6)
            self.browser.find_element_by_css_selector("#btnLogin > span > span").click()

            code = raw_input("Enter Auth Code:")
            self.browser.find_element_by_id("twofactorCode").clear()
            self.browser.find_element_by_id("twofactorCode").send_keys(code)
            self.pause(2, 4)
            self.browser.find_element_by_css_selector("#btnTFAVerify > span > span").click()

        self.pause(20, 30) # Wait for the page to load

        self.input_controller.move_mouse(319, 500)
        self.input_controller.click()
        self.pause(1, 2)
        self.input_controller.send_string(answer)
        self.pause(2, 3)
        self.input_controller.move_mouse(345, 536)
        self.input_controller.click()

        self.save_cookies()

        # self.browser.find_element_by_css_selector("input.futPhishingTextBoxTyped").clear()
        # self.browser.find_element_by_css_selector("input.futPhishingTextBoxTyped").send_keys(answer)
        # self.pause(2, 3)
        # self.browser.find_element_by_css_selector("input.futPhishingButtonArrow.futPhishingButton").click()

        while True:
            print self.input_controller.mouse_position()
            time.sleep(3)

class HIDInput_OSX(object):
    def __init__(self, correction=(0,0)):
        self.hwnd = None
        self.correction = correction

    def window_rect(self):
        return (0, 0, 1440, 900)

    def set_window(self, windowTitle):
        return True

    def activate_window(self):
        return True

    def window_location(self):
        return self.window_rect()[:2]

    def move_mouse(self, x, y):
        pyautogui.moveTo(x + self.correction[0], y + self.correction[1])

    def click(self):
        pyautogui.click()

    def mouse_position(self):
        return pyautogui.position()

    def send_string(self, string):
        pyautogui.typewrite(string, interval=0.2)

class HIDInput_Windows(object):
    def __init__(self, correction=(0,0)):
        import win32api
        import win32con
        import win32gui
        import ctypes
        import win32process
        self.hwnd = None
        self.correction = correction

    def window_rect(self):
        return win32gui.GetWindowRect(self.hwnd)

    def set_window(self, windowTitle):
        # Search all open Windows
        EnumWindows = ctypes.windll.user32.EnumWindows
        EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
        GetWindowText = ctypes.windll.user32.GetWindowTextW
        GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
        IsWindowVisible = ctypes.windll.user32.IsWindowVisible

        titles = []
        def foreach_window(hwnd, lParam):
            if IsWindowVisible(hwnd):
                length = GetWindowTextLength(hwnd)
                buff = ctypes.create_unicode_buffer(length + 1)
                GetWindowText(hwnd, buff, length + 1)
                titles.append(buff.value)
            return True
        EnumWindows(EnumWindowsProc(foreach_window), 0)
        #Search each window for Puzzle Pirates
        windows = []
        for title in titles:
            if (title.find(windowTitle)>-1):
                windows.append(win32gui.FindWindow(None, title)) #Find window and return Handle
        if (len(windows) == 0):
            raise Exception(windowTitle , ' Not Found')
        elif (len(windows) == 1):
            self.hwnd = windows[0]
            return True
        else:
            print "Found more than one matching window"
        return False

    def activate_window(self):
        if (win32gui.SystemParametersInfo(win32con.SPI_GETFOREGROUNDLOCKTIMEOUT) != 0):
            win32gui.SystemParametersInfo(win32con.SPI_SETFOREGROUNDLOCKTIMEOUT, 0, win32con.SPIF_SENDWININICHANGE | win32con.SPIF_UPDATEINIFILE)
        fgwin = win32gui.GetForegroundWindow()
        fg = win32process.GetWindowThreadProcessId(fgwin)[0]
        current = win32api.GetCurrentThreadId()
        if current != fg:
            win32process.AttachThreadInput(fg, current, True)
            win32gui.SetForegroundWindow(self.hwnd)
            win32process.AttachThreadInput(fg, win32api.GetCurrentThreadId(), False)

    def window_location(self):
        return self.window_rect()[:2]

    def move_mouse(self, x, y):
        window_offset = self.window_location()
        pyautogui.moveTo(x + self.correction[0] + window_offset[0], y + self.correction[1] + window_offset[1])

    def click(self):
        pyautogui.click()

    def mouse_position(self):
        pos = pyautogui.position()
        return pos[0] + self.correction[0], pos[1], self.correction[1]

    def send_string(self, string):
        pyautogui.typewrite(string, interval=0.2)