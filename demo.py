from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from appium.options.android import UiAutomator2Options
from selenium.common.exceptions import TimeoutException
import time
import subprocess
import sys
import ctypes
import time

import logging
from datetime import datetime

# Set up logging with both file and console output
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/booking_log_{datetime.now().strftime("%Y%m%d")}.txt'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def is_appium_running():
    """Check if Appium server is running"""
    try:
        import requests
        from requests.exceptions import ConnectionError
        try:
            response = requests.get('http://127.0.0.1:4723/status', timeout=5)
            return response.status_code == 200
        except ConnectionError:
            logger.info("Appium is not running (connection refused)")
            return False
        except Exception as e:
            logger.error(f"Error checking Appium status: {str(e)}")
            return False
    except Exception as e:
        logger.error(f"Error in is_appium_running: {str(e)}")
        return False

def start_appium():
    """Start Appium server"""
    try:
        logger.info("Starting Appium server...")
        
        # Use start command to open new command window and run Appium
        start_command = 'start cmd.exe /c "conda activate ds && appium"'
        subprocess.run(start_command, shell=True)
        
        # Wait for Appium to start
        logger.info("Waiting for Appium to start...")
        attempts = 10  # Increase attempts to 10
        for i in range(attempts):
            if is_appium_running():
                logger.info("Appium server started successfully")
                return True
            logger.info(f"Appium start attempt {i+1}/{attempts}")
            time.sleep(5)
        
        logger.error("Failed to start Appium server after multiple attempts")
        return False
    except Exception as e:
        logger.error(f"Error starting Appium: {str(e)}")
        return False

def get_avd_name():
    try:
        result = subprocess.run([r"emulator.exe", "-list-avds"], 
                              capture_output=True, text=True)
        if result.stdout:
            avd_names = result.stdout.strip().split('\n')
            logger.info(f"Found AVDs: {avd_names}")
            return avd_names[0]  # Return first AVD name
        else:
            logger.error("No AVDs found")
            return None
    except Exception as e:
        logger.error(f"Error getting AVD name: {str(e)}")
        return None


def start_android_emulator():
    """Start Android Emulator"""
    try:
        logger.info("Starting Android Emulator...")
        print("start android")
        
        # Kill processes more thoroughly
        try:
            subprocess.run(['adb', 'emu', 'kill'], 
                          stdout=subprocess.DEVNULL, 
                          stderr=subprocess.DEVNULL)
            time.sleep(5)  # Wait for emulator to fully shut down
            
            # Kill any remaining processes
            subprocess.run(['taskkill', '/F', '/IM', 'qemu-system-x86_64.exe', '/T'], 
                          stdout=subprocess.DEVNULL, 
                          stderr=subprocess.DEVNULL)
            subprocess.run(['taskkill', '/F', '/IM', 'emulator.exe', '/T'], 
                          stdout=subprocess.DEVNULL, 
                          stderr=subprocess.DEVNULL)
            subprocess.run(['adb', 'kill-server'], 
                          stdout=subprocess.DEVNULL, 
                          stderr=subprocess.DEVNULL)
            
            time.sleep(5)  # Wait for all processes to be killed
        except Exception as e:
            logger.error(f"Error killing processes: {str(e)}")
        
        # Delete lock files with a different approach
        import glob
        import os
        lock_files = glob.glob(r"..\android\avd\Medium_Phone_API_35.avd\*.lock")
        for file in lock_files:
            try:
                if os.path.exists(file):
                    os.chmod(file, 0o777)  # Give full permissions
                    os.remove(file)
                    logger.info(f"Removed lock file: {file}")
            except Exception as e:
                logger.error(f"Error removing lock file {file}: {str(e)}")
                # If we can't delete, try to empty the file
                try:
                    with open(file, 'w') as f:
                        pass
                except Exception as e2:
                    logger.error(f"Error emptying lock file: {str(e2)}")
        
        time.sleep(5)  # Wait after deleting lock files
        
        # Restart ADB server
        subprocess.run(['adb', 'start-server'])
        time.sleep(2)
        
        # Path to emulator
        emulator_path = r"emulator.exe"
        
        # Get AVD name
        avd_name = get_avd_name()
        if not avd_name:
            raise Exception("No AVD found")
            
        logger.info(f"Starting emulator with AVD: {avd_name}")
        # Remove -wipe-data flag and add -no-window for Task Scheduler
        start_command = f'"{emulator_path}" -avd {avd_name}'
        
        subprocess.Popen(start_command, shell=True)
        
        # Wait for emulator to start
        logger.info("Waiting for emulator to start...")
        # Use adb to check if device is online
        for i in range(12):  # Try for 60 seconds
            try:
                result = subprocess.run(['adb', 'devices'], capture_output=True, text=True)
                if 'emulator-5554' in result.stdout and 'device' in result.stdout:
                    logger.info("Emulator started successfully")
                    return True
            except Exception:
                pass
            logger.info(f"Waiting for emulator... Attempt {i+1}/12")
            time.sleep(5)
        
        logger.error("Failed to start emulator")
        return False
            
    except Exception as e:
        logger.error(f"Error starting emulator: {str(e)}")
        return False


def restart_adb():
    """Restart ADB server"""
    try:
        logger.info("Restarting ADB server...")
        subprocess.run(['adb', 'kill-server'])
        time.sleep(2)
        subprocess.run(['adb', 'start-server'])
        time.sleep(3)
        logger.info("ADB server restarted")
    except Exception as e:
        logger.error(f"Error restarting ADB server: {str(e)}")


def wake_up_screen():
    """Wake up the screen if it's in sleep mode"""
    try:
        ctypes.windll.kernel32.SetThreadExecutionState(0x80000000 | 0x00000001 | 0x00000002)
        logger.info("Waking up screen...")
        time.sleep(5)  # Increased wait time
        restart_adb()  # Restart ADB after wake
    except Exception as e:
        logger.error(f"Error waking up screen: {str(e)}")

def check_wifi_connection():
    """Check if connected to WiFi"""
    try:
        result = subprocess.run(['netsh', 'wlan', 'show', 'interfaces'], 
                              capture_output=True, text=True)
        if "State                  : connected" in result.stdout:
            logger.info("WiFi connected")
            return True
        logger.warning("WiFi not connected")
        return False
    except Exception as e:
        logger.error(f"Error checking WiFi: {str(e)}")
        return False

def connect_to_wifi(ssid="Sharon_Home(5GHz)", password="simei167"):
    """Connect to specified WiFi network"""
    try:
        if not check_wifi_connection():
            connect_command = f'netsh wlan connect name="{ssid}"'
            subprocess.run(connect_command, shell=True)
            time.sleep(5)  # Wait for connection
            if check_wifi_connection():
                print(f"Successfully connected to {ssid}")
                logger.info("Successfully connected to wifi")
                return True
            else:
                print(f"Failed to connect to {ssid}")
                return False
        else:
            print("Already connected to WiFi")
            return True
    except Exception as e:
        logger.error(f"Error connecting to WiFi: {str(e)}")
        return False


# Configuration constants
APPIUM_SERVER = 'http://127.0.0.1:4723'
APP_PACKAGE = '[YOUR APP PACKAGE]'
APP_ACTIVITY = '[YOUR APP ACTIVITY]'
DEVICE_NAME = '[YOUR DEVICE NAME]'
WAIT_TIME = 10
EMAIL = "[EMAIL]"
PASSWORD = "[PASSWORD]"

# Slot coordinates mapping
SLOT_COORDINATES = {
    1: (500, 650),   # 1st slot
    2: (516, 1003),  # 2nd slot
    3: (461, 1372),  # 3rd slot
    4: (388, 1718),  # 4th slot
    5: (377, 2017),   # 5th slot
    6: (386, 2154)
}

class GlofoxBooker:
    def __init__(self, day_of_week="Sun", tap_coordinates=(516, 1003), categories_to_skip=6, slot_number=1):
        # Check WiFi connection
        if check_wifi_connection():
            logger.info("Connected to wifi, will proceed")
        if not check_wifi_connection():
            logger.error("No WiFi connection detected, attempting to connect...")
            if not connect_to_wifi():
                logger.error("Failed to connect to WiFi")
                raise Exception("Could not establish WiFi connection")


        self.day_of_week = day_of_week
        self.tap_coordinates = tap_coordinates
        self.slot_number = slot_number
        self.categories_to_skip = categories_to_skip
        self.tap_coordinates = SLOT_COORDINATES.get(slot_number, (516, 1003))  # Default to 2nd slot if invalid
        self.driver = None
        self.setup_driver()

    def restart_process(self):
        logger.error("Email field not found, restarting process...")
        try:
            self.driver.quit()
        except:
            print("Driver already closed")
        time.sleep(2)
        self.__init__(
            day_of_week=self.day_of_week,
            categories_to_skip=self.categories_to_skip,
            slot_number=self.slot_number
        )
        self.run_booking_flow()

    def setup_driver(self, max_retries=3):
        for attempt in range(max_retries):
            try:
                options = UiAutomator2Options()
                options.platform_name = 'Android'
                options.device_name = DEVICE_NAME
                options.automation_name = 'UiAutomator2'
                options.app_package = APP_PACKAGE
                options.app_activity = APP_ACTIVITY
                options.no_reset = True
                
                # Clear app state and connect to Appium
                subprocess.run(['adb', 'shell', 'pm', 'clear', APP_PACKAGE])
                logger.info("Cleared app state")
                time.sleep(10)

                
                self.driver = webdriver.Remote(APPIUM_SERVER, options=options)
                logger.info("Connected to Appium server")
                return True
            except Exception as e:
                logger.error(f"Attempt {attempt + 1}/{max_retries} failed: {str(e)}")
                if attempt < max_retries - 1:
                    logger.info("Restarting ADB and retrying...")
                    restart_adb()
                    time.sleep(5)
                else:
                    raise Exception("Failed to setup driver after multiple attempts")

    def handle_permission_popup(self):
        try:
            permission_dialog = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((
                    AppiumBy.ID,
                    "com.android.permissioncontroller:id/grant_dialog"
                ))
            )
            allow_button = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((
                    AppiumBy.ID,
                    "com.android.permissioncontroller:id/permission_allow_button"
                ))
            )
            allow_button.click()
            logger.info("Handled permission popup")

        except TimeoutException:
            logger.error("No permission popup found, restarting process...")
            self.restart_process()
            return  # Add return to prevent continuing with the process


    def search_and_login(self):
        # Find and interact with search
        search_field = WebDriverWait(self.driver, WAIT_TIME).until(
            EC.presence_of_element_located((
                AppiumBy.XPATH,
                "//android.widget.EditText[@text='Find your studio or gym']"
            ))
        )
        search_field.click()
        time.sleep(15)
        
        search_field = WebDriverWait(self.driver, WAIT_TIME).until(
            EC.presence_of_element_located((
                AppiumBy.CLASS_NAME,
                "android.widget.EditText"
            ))
        )
        search_field.send_keys("[YOUR STUDIO NAME]")
        time.sleep(15)
        

        # Click search result
        try:
            result = WebDriverWait(self.driver, WAIT_TIME).until(
                EC.presence_of_element_located((
                    AppiumBy.XPATH,
                    "//android.widget.TextView[@text='[YOUR STUDIO NAME]']"
                ))
            )
            result.click()
            logger.info("Found")
            time.sleep(5)
        except TimeoutException:
            logger.error("Not found in search results, restarting process...")
            self.restart_process()
            return  # Add return to prevent continuing with the rest of the method
        
        # Check for email field and restart if not found
        try:
            email_field = WebDriverWait(self.driver, 5).until(  # Shorter timeout for quick check
                EC.presence_of_element_located((
                    AppiumBy.ACCESSIBILITY_ID,
                    "Enter your email address"
                ))
            )
            # If email field is found, proceed with login
            self.enter_credentials()
            self.click_login_button()
        except TimeoutException:
            self.restart_process()

    def enter_credentials(self):
        email_field = WebDriverWait(self.driver, WAIT_TIME).until(
            EC.presence_of_element_located((
                AppiumBy.ACCESSIBILITY_ID,
                "Enter your email address"
            ))
        )
        email_field.click()
        email_field.send_keys(EMAIL)
        
        password_field = WebDriverWait(self.driver, WAIT_TIME).until(
            EC.presence_of_element_located((
                AppiumBy.ACCESSIBILITY_ID,
                "Enter your password"
            ))
        )
        password_field.click()
        password_field.send_keys(PASSWORD)
        

    def click_login_button(self):
        login_button = WebDriverWait(self.driver, WAIT_TIME).until(
            EC.presence_of_element_located((
                AppiumBy.ACCESSIBILITY_ID,
                "Tap here to Login to continue"
            ))
        )
        login_button.click()
        logger.info(f"Clicked login button")

        time.sleep(3)

    def book_class(self):
        # Click booking view
        booking_view = WebDriverWait(self.driver, WAIT_TIME).until(
            EC.presence_of_element_located((
                AppiumBy.XPATH,
                "//android.view.View[@bounds='[100,210][980,770]']"
            ))
        )
        booking_view.click()
        logger.error(f"Clicked booking view")

        # Select day
        day_button = WebDriverWait(self.driver, WAIT_TIME).until(
            EC.presence_of_element_located((
                AppiumBy.XPATH,
                f"//android.widget.TextView[@text='{self.day_of_week}']"
            ))
        )
        day_button.click()
        logger.info(f"Clicked on {self.day_of_week}")

        time.sleep(3)

        timestamp = time.strftime("%Y%m%d_%H%M%S")
        screenshot_name = f"screenshots/booking_confirmation_{timestamp}.png"
        self.driver.save_screenshot(screenshot_name)
        logger.info(f"saved pre-scrolling screenshot as {screenshot_name}")
        time.sleep(1)

        # Scroll
        try:
            for _ in range(self.categories_to_skip):
                scroll_command = (
                    'new UiScrollable(new UiSelector().scrollable(true)).setAsVerticalList()'
                    '.scrollForward()'
                )
                self.driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, scroll_command)
                time.sleep(0.5)
            logger.info("Performed scroll")
        except Exception as e:
            logger.error(f"Scroll error: {str(e)}")

        time.sleep(2)

        timestamp = time.strftime("%Y%m%d_%H%M%S")
        screenshot_name = f"screenshots/booking_confirmation_{timestamp}.png"
        self.driver.save_screenshot(screenshot_name)
        logger.info(f"saved post-scrolling screenshot as {screenshot_name}")

        # Tap coordinates
        self.driver.execute_script('mobile: clickGesture', 
                                {'x': self.tap_coordinates[0], 
                                'y': self.tap_coordinates[1]})
        logger.info(f"Tapped on coordinates {self.tap_coordinates}")

        # Complete booking process
        self.complete_booking()
                
    def complete_booking(self):
        book_button = WebDriverWait(self.driver, WAIT_TIME).until(
            EC.presence_of_element_located((
                AppiumBy.ACCESSIBILITY_ID,
                "Tap here to undefined"
            ))
        )
        time.sleep(2)
        book_button.click()
        logger.info("Clicked booking button")
        time.sleep(2)

        final_button = WebDriverWait(self.driver, WAIT_TIME).until(
            EC.presence_of_element_located((
                AppiumBy.XPATH,
                "//android.widget.Button[@content-desc='Tap here to boo']/android.view.View"
            ))
        )
        final_button.click()
        time.sleep(1)
        final_button.click()
        logger.info("Completed final booking step")

    def run_booking_flow(self):
        try:
            time.sleep(5)  # Initial wait for app load
            self.handle_permission_popup()
            self.search_and_login()
            self.book_class()
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
        finally:
            try:
                self.driver.quit()
                logger.info("Session ended successfully")
            except:
                logger.info("Session already ended")

def stop_emulator():
    """Stop Android Emulator"""
    try:
        logger.info("Stopping Android Emulator...")
        subprocess.run(['adb', 'emu', 'kill'])
        time.sleep(2)
        logger.info("Emulator stopped")
    except Exception as e:
        logger.error(f"Error stopping emulator: {str(e)}")

def stop_appium():
    """Stop Appium server"""
    try:
        logger.info("Stopping Appium server...")
        subprocess.run(['taskkill', '/F', '/IM', 'node.exe'], 
                     stdout=subprocess.DEVNULL, 
                     stderr=subprocess.DEVNULL)
        time.sleep(2)
        logger.info("Appium server stopped")
    except Exception as e:
        logger.error(f"Error stopping Appium: {str(e)}")


if __name__ == "__main__":
    try:
        start_time = datetime.now()
        logger.info(f"====== Starting booking script at {start_time} ======")
        
        # Start Android Emulator first
        if not start_android_emulator():
            raise Exception("Could not start Android Emulator")
            
        # Give emulator time to fully boot up
        logger.info("Waiting for emulator to fully boot...")
        time.sleep(30)  # Wait longer for emulator to fully boot
        
        # Check Appium status
        if not is_appium_running():
            logger.info("Appium not running, attempting to start...")
            if not start_appium():
                raise Exception("Could not start Appium server")
            time.sleep(10)  # Wait for Appium to fully initialize
        
        wake_up_screen()
        time.sleep(10)  # Additional wait after wake up
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                booker = GlofoxBooker(
                    day_of_week="Sat",
                    categories_to_skip=0, # 6th
                    slot_number=3
                )
                booker.run_booking_flow()
                break  # If successful, exit the retry loop
            except Exception as e:
                logger.error(f"Attempt {attempt + 1}/{max_retries} failed: {str(e)}")
                if attempt < max_retries - 1:
                    logger.info("Restarting and retrying...")
                    restart_adb()
                    
                    # Check emulator and Appium again before retry
                    if not start_android_emulator():
                        raise Exception("Could not restart Android Emulator")
                    time.sleep(30)  # Wait for emulator
                    
                    if not is_appium_running():
                        if not start_appium():
                            raise Exception("Could not restart Appium server")
                        time.sleep(10)
                    
                    time.sleep(5)
                else:
                    raise  # Re-raise the last exception if all retries failed

        end_time = datetime.now()
        duration = end_time - start_time
        logger.info(f"====== Script completed successfully at {end_time} ======")
        logger.info(f"Total execution time: {duration}")

    except Exception as e:
        logger.error(f"====== Script failed with error: {str(e)} ======", exc_info=True)
    finally:
        try:
            stop_emulator()  # Stop the emulator
            stop_appium()    # Stop the Appium server
            logger.info("====== Script execution ended ======\n")
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")