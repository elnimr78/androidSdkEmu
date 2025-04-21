from adb_shell.adb_device import AdbDeviceTcp
import xml.etree.ElementTree as ET
import re
import time
import os 
import random 
import xml.etree.ElementTree as et

class device :
    
    @staticmethod
    def connect(host="localhost", port=5555):
        device = AdbDeviceTcp(host, port)
        try:
            device.connect()
            if device.available:
                return device
        except Exception as e:
            print(f"[-] ADB Connection failed to {host}:{port} except: {e}")
        return None
    
    @staticmethod
    def connect_r(host="localhost", port=5555, max_retries=5):
        device = AdbDeviceTcp(host, port)
        for attempt in range(max_retries):
            try:
                device.connect()
                if device.available:
                    #print(f"[+] Connected to {host}:{port} ADB (Attempt {attempt+1})")
                    return device
            except Exception as e:
                print(f"[-] ADB Connection failed {host}:{port} (Attempt {attempt+1}): {e}")
            time.sleep(3)
        
        print(f"[-] Failed to connect to ADB {host}:{port} after multiple attempts.")
        return None
    
    @staticmethod
    def disconnect(device):
        try:
            if device:
                device.close()
        except Exception as e:
            print("[-][disconnect] Failed to disconnect device:", e)


class app :

    @staticmethod    
    def install_app(apk, package_name,_host="localhost",_port=5555):
        dv = device.connect(_host,_port)
        if not dv:
            print("[-][install_app] No ADB device connected.")
            return False
        
        if app.is_installed(package_name):
            print(f"[+][install_app] {package_name} is already installed.")
            device.disconnect(dv) 
            return "Already Installed"


        if not os.path.exists(apk):
            print(f"[-][install_app] APK file not found: {apk}")
            device.disconnect(dv)
            return "APK Not Found"
        
        apk_filename = os.path.basename(apk) 
        bs_apk_path = f"/data/local/tmp/{apk_filename}"  # Path inside BlueStacks

        try:
            print(f"[+][install_app] Pushing APK ...")
            dv.push(apk, bs_apk_path)  
            time.sleep(2)
            print(f"[+][install_app] Installing APK from {bs_apk_path}")
            install_output = dv.shell(f"pm install -r {bs_apk_path}")
            time.sleep(0.2)
            print(f"[+][install_app] Install output: {install_output}")
            device.disconnect(dv) 
            return install_output
        except Exception as e:
            print(f"[-][install_app] Install error: {e}")
            device.disconnect(dv) 
            return "Install Faild"
        
    @staticmethod
    def is_installed(package_name,_host="localhost",_port=5555):
        dv = device.connect(_host,_port)
        if not dv:
            print("[-][is_installed] No ADB device connected.")
            return False
        try:
            output = dv.shell("pm list packages")
            time.sleep(0.2)
            installed_packages = output.split("\n")
            device.disconnect(dv) 
            return any(f"package:{package_name}" in pkg for pkg in installed_packages)
        except Exception as e:
            print(f"[-][is_installed] exception: {e}")
            device.disconnect(dv) 
            return False
    
    @staticmethod
    def uninstall_app(package_name,_host="localhost",_port=5555):
        dv = device.connect(_host,_port)
        if not dv:
            print("[-][uninstall_app] No ADB device connected.")
            return False
        try:
            uninstall_output = dv.shell(f"pm uninstall {package_name}")
            time.sleep(0.2)
            print(f"[+][uninstall_app] Uninstalled Success {package_name}")
            print(uninstall_output) 
            device.disconnect(dv) 
            return uninstall_output.strip() == "Success"
        except Exception as e:
            print(f"[-][uninstall_app] Uninstalled Error {e}")
            device.disconnect(dv) 
            return False  

    @staticmethod
    def launch_app(package_name,_host="localhost",_port=5555):
        dv = device.connect(_host,_port)
        if not dv:
            print("[-][launch_app] No ADB device connected.")
            return False
        try:
            dv.shell(f"monkey -p {package_name} -c android.intent.category.LAUNCHER 1")
            time.sleep(0.2)
            print(f"[+][launch_app] Launched {package_name} successfully!")
            device.disconnect(dv) 
            return True
        except Exception as e:
            device.disconnect(dv) 
            print(f"[-][launch_app] Failed to launch {package_name}: {e}")
            return False 

    @staticmethod
    def terminate_app(package_name,_host="localhost",_port=5555):
        dv = device.connect(_host,_port)
        if not dv:
            print("[-][uninstall_app] No ADB device connected.")
            return False
        try:
            print(f"[+][terminate_app] Terminating {package_name}...")
            dv.shell(f"am force-stop {package_name}")
            time.sleep(0.2)
            print(f"[+][terminate_app] {package_name} has been terminated.")
            device.disconnect(dv) 
            return True
        except Exception as e:
            print(f"[-][terminate_app] Error terminating app: {e}")
            device.disconnect(dv) 
            return False

    @staticmethod
    def is_running(package_name,_host="localhost",_port=5555):
        dv = device.connect(_host,_port)
        if not dv:
            print("[-][is_running] No ADB device connected.")
            return False
        try:
            output = dv.shell(f"pidof {package_name}")  # Get process ID
            
            device.disconnect(dv) 
            return bool(output.strip())  # If output is not empty, the app is running
        except Exception as e:
            print(f"[-][is_running] Error checking if app is running: {e}")
            device.disconnect(dv) 
            return False
        
    @staticmethod
    def is_running_ps(package_name,_host="localhost",_port=5555):
        """Alternative method using `ps` command to check if an app is running."""
        dv = device.connect(_host,_port)  
        if not dv:
            print("[-][is_running_ps] No ADB device connected.")
            return False
        try:
            output = dv.shell("ps | grep " + package_name)
            time.sleep(0.2)
            device.disconnect(dv) 
            return package_name in output  # If found, app is running
        except Exception as e:
            print(f"[-][is_running_ps] Error checking app process: {e}")
            device.disconnect(dv) 
            return False

    @staticmethod
    def is_app_fully_loaded(package_name, timeout=30,_host="localhost",_port=5555):
        """Waits until an app is fully loaded by checking window focus and process ID."""
        dv = device.connect(_host,_port)  
        if not dv:
            print("[-][is_app_fully_loaded] No ADB device connected.")
            return False

        print(f"[+] Waiting for {package_name} to fully load...")

        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                # Step 1: Check if app is in the foreground
                foreground_output = dv.shell("dumpsys window | grep mCurrentFocus")
                time.sleep(0.2)
                if package_name in foreground_output:
                    print(f"[✅] {package_name} is in the foreground.")

                # Step 2: Check if app process is running
                process_output = dv.shell(f"pidof {package_name}")
                time.sleep(0.2)
                if process_output.strip():
                    print(f"[✅] {package_name} process is active.")

                # If both conditions are met, app is fully loaded
                if package_name in foreground_output and process_output.strip():
                    print(f"[🎉][is_app_fully_loaded] {package_name} is fully loaded!")
                    device.disconnect(dv) 
                    return True

            except Exception as e:
                print(f"[-][is_app_fully_loaded] Error checking app status: {e}")


            time.sleep(1)  # Wait before checking again

        print(f"[-] Timeout: {package_name} did not fully load in {timeout} seconds.")
        device.disconnect(dv) 
        return False

    @staticmethod
    def is_app_fully_loaded_window(package_name, timeout=30,_host="localhost",_port=5555):
        """Waits until an app is fully loaded by checking top window activity."""
        dv = device.connect(_host,_port)  
        if not dv:
            print("[-][is_app_fully_loaded_W] No ADB device connected.")
            return False

        print(f"[+] Waiting for {package_name} to be in the foreground...")

        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                output = dv.shell("dumpsys window windows | grep mCurrentFocus")
                time.sleep(0.2)
                if package_name in output:
                    print(f"[✅][is_app_fully_loaded_W] {package_name} is fully loaded and in focus!")
                    return True

            except Exception as e:
                print(f"[-][is_app_fully_loaded_W] Error checking window focus: {e}")

            time.sleep(1)  

        print(f"[-][is_app_fully_loaded_W] Timeout: {package_name} did not fully load in {timeout} seconds.")
        return False

    @staticmethod
    def get_running_app(_host="localhost",_port=5555):
        dv = device.connect(_host,_port)  
        if not dv:
            print("[-][get_running_app] No ADB device connected.")
            return False

        try:
            # Get the list of running activities
            output = dv.shell("dumpsys activity activities")
            time.sleep(0.2)
            # Debugging: Print raw output
            #print(f"[+] Raw ADB Output:\n{output}")

            # Look for the focused activity
            for line in output.splitlines():
                if "mResumedActivity" in line or "topResumedActivity" in line:
                    #print(f"[+] Matched Line: {line}")  # Debugging output
                    package_name = line.split()[2].split("/")[0]  # Extract package name
                    print(f"[+] Current running app: {package_name}")
                    device.disconnect(dv) 
                    return package_name

            print("[-][get_running_app] Could not determine the running app.")
            device.disconnect(dv) 
            return None
        except Exception as e:
            print(f"[-][get_running_app] Error getting running app: {e}")
            device.disconnect(dv) 
            return None

    @staticmethod
    def launch_play_store(_host="localhost",_port=5555):
        dv = device.connect(_host,_port)  
        if not dv:
            print("[-][launch_play_store] No ADB device connected.")
            return False
        try:
            print("[+][launch_play_store] Launching Google Play Store...")
            dv.shell("monkey -p com.android.vending -c android.intent.category.LAUNCHER 1")
            time.sleep(0.2)
            print("[+][launch_play_store] Google Play Store launched successfully!")
            device.disconnect(dv) 
            return True
        except Exception as e:
            print(f"[-][launch_play_store] Error launching Play Store: {e}")
            device.disconnect(dv) 
            return False


class prop:
   
    @staticmethod
    def change_device_profile(manufacturer="Samsung", brand="Galaxy", model="S23",_host="localhost",_port=5555):
        dv = device.connect(_host,_port)  
        if not dv:
            print("[-][launch_play_store] No ADB device connected.")
            return False

        try:
            # Apply changes using ADB shell properties
            dv.shell(f"setprop ro.product.manufacturer \"{manufacturer}\"")
            time.sleep(0.2)
            dv.shell(f"setprop ro.product.brand \"{brand}\"")
            time.sleep(0.2)
            dv.shell(f"setprop ro.product.model \"{model}\"")
            time.sleep(0.2)

            # Verify changes
            new_manufacturer = dv.shell("getprop ro.product.manufacturer").strip()
            time.sleep(0.2)
            new_brand = dv.shell("getprop ro.product.brand").strip()
            time.sleep(0.2)
            new_model = dv.shell("getprop ro.product.model").strip()
            time.sleep(0.2)

            print(f"[✅] New Manufacturer: {new_manufacturer}")
            time.sleep(0.2)
            print(f"[✅] New Brand: {new_brand}")
            time.sleep(0.2)
            print(f"[✅] New Model: {new_model}")
            time.sleep(0.2)

            device.disconnect(dv) 
            return True
        except Exception as e:
            print(f"[-] Error changing device profile: {e}")
            device.disconnect(dv) 
            return False
   
    @staticmethod
    def verify_device_profile(expected_manufacturer, expected_brand, expected_model,_host="localhost",_port=5555):
        dv = device.connect(_host,_port)  
        if not dv:
            print("[-][verify_device_profile] No ADB device connected.")
            return False

        # Get current values
        current_manufacturer = dv.shell("getprop ro.product.manufacturer").strip() 
        time.sleep(0.2)
        current_brand = dv.shell("getprop ro.product.brand").strip()
        time.sleep(0.2)
        current_model = dv.shell("getprop ro.product.model").strip()
        time.sleep(0.2)

        print(f"📢 Verifying Device Profile:")
        print(f"    📌 Manufacturer: {current_manufacturer} (Expected: {expected_manufacturer})")
        print(f"    📌 Brand: {current_brand} (Expected: {expected_brand})")
        print(f"    📌 Model: {current_model} (Expected: {expected_model})")

        # Check if values match
        if (current_manufacturer == expected_manufacturer and
            current_brand == expected_brand and
            current_model == expected_model):
            print("[✅][verify_device_profile] Profile successfully changed!")
            device.disconnect(dv) 
            return True
        else:
            print("[-][verify_device_profile] Profile change failed or reverted.")
            device.disconnect(dv) 
            return False
   
    @staticmethod
    def get_device_profile(_host="localhost",_port=5555):
        dv = device.connect(_host,_port)  
        if not dv:
            print("[-][get_device_profile] No ADB device connected.")
            return False

        # Get current values
        current_manufacturer = dv.shell("getprop ro.product.manufacturer").strip()
        time.sleep(0.2)
        current_brand = dv.shell("getprop ro.product.brand").strip()
        time.sleep(0.2)
        current_model = dv.shell("getprop ro.product.model").strip()
        time.sleep(0.2)

        print(f"📢Device Profile:")
        print(f"    📌 Manufacturer: {current_manufacturer})")
        print(f"    📌 Brand: {current_brand} )")
        print(f"    📌 Model: {current_model}")
        device.disconnect(dv) 
   
    @staticmethod
    def change_resolution(width=1280, height=720, dpi=240,_host="localhost",_port=5555):
        dv = device.connect(_host,_port)  
        if not dv:
            print("[-][get_device_profile] No ADB device connected.")
            return False
        try:
            print(f"[+][get_device_profile] Setting resolution to {width}x{height} and DPI to {dpi}...")
            dv.shell(f"wm size {width}x{height}")  # Change screen size
            time.sleep(0.2)
            dv.shell(f"wm density {dpi}")  # Change DPI
            time.sleep(0.2)
            print("[+][get_device_profile] Resolution changed successfully!")
            device.disconnect(dv) 
            return True
        except Exception as e:
            print(f"[-][get_device_profile] Error changing resolution: {e}")
            device.disconnect(dv) 
            return False
    
    @staticmethod  
    def is_google_account_exists(_host="localhost",_port=5555):
        dv = device.connect(_host,_port)  
        if not dv:
            print("[-][get_device_profile] No ADB device connected.")
            return False
        try:
            # Run ADB command to list accounts
            output = dv.shell("content query --uri content://accounts/accounts")
            time.sleep(0.2)
            # Check if any Google account is found
            device.disconnect(dv) 
            return "com.google" in output  # ✅ True if Google account exists, False otherwise

        except Exception as e:
            print(f"[-][get_device_profile] Error checking Google account: {e}")
            device.disconnect(dv) 
            return False


class actions:

    @staticmethod
    def tap(x=None, y=None , bounds = None , threshold=10,_host="localhost",_port=5555):
        dv = device.connect(_host,_port)  
        if not dv:
            print("[-][tap] No ADB device connected.")
            return False

        if bounds: 
            match = re.search(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", bounds)
            if match:
                x1, y1, x2, y2 = map(int, match.groups())
                x = (x1 + x2) // 2  
                y = (y1 + y2) // 2  
        
        rand_x = random.uniform( x - threshold, x + threshold  )
        rand_y = random.uniform( y - threshold, y + threshold  )
        dv.shell(f"input tap {rand_x} {rand_y}")        
        time.sleep(0.2)
        print(f"[+][tap] Tapped at: ({rand_x}, {rand_y})")
      
    @staticmethod
    def swap(start_x,start_y,end_x,end_y,_host="localhost",_port=5555) :
        dv = device.connect(_host,_port)  
        if not dv:
            print("[-][tap] No ADB device connected.")
            return False
        try :
            dv.shell(f"input swipe {start_x} {start_y} {end_x} {end_y}")
            print(f"[+][swap] Swapped Sent : {start_x} {start_y} {end_x} {end_y} .")
            device.disconnect()
            return True 
        except Exception as e :
            print(f"[-][swap] Error: {e}")
            device.disconnect()
            return False  
        
    @staticmethod
    def write_text(text,_host="localhost",_port=5555):
        dv = device.connect(_host,_port)  
        if not dv:
            print("[-][write_text] No ADB device connected.")
            return False
        try:
            dv.shell(f'input text {text}')
            time.sleep(0.2)
        except Exception as e :
            print(f"[-][write_text] Error: {e}")
            return False  
       
            
class ui:

    @staticmethod
    def read_ui(filename="ui.xml",_host="localhost",_port=5555):
        dv = device.connect(_host,_port)
        if not dv:
            print("[-][read_ui] No ADB device connected.")
            return False
        try:
            dv.shell(f"uiautomator dump /sdcard/{filename}")
            time.sleep(0.2)
        except Exception as e:
            print(f"[-][read_ui] Error Dumping {filename} file: {e}")
            device.disconnect(dv)
            return False
        try:
            # Pull UI XML to local machine
            dv.pull(f"/sdcard/{filename}", f"{filename}")
            time.sleep(0.2)
            #print(f"[+][read_ui] UI XML extracted {filename} successfully!")
            device.disconnect(dv)
            return True
        except Exception as e:
            print(f"[-][read_ui] Error Pulling {filename} file: {e}")
            device.disconnect(dv)
            return False

    @staticmethod
    def find(query, type="text", filename="ui.xml"):
        try:
            tree = et.parse(filename)
            root = tree.getroot()
            
            for node in root.iter("node"):
                if node.attrib.get(type) == query:
                    return True, node.attrib.get("bounds") 
                           
            return False, None  
            
        except Exception as e:
            print(f"[-][find] exception: {e}")
            return False, None




