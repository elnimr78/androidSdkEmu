from adb_shell.adb_device import AdbDeviceTcp
from adb_shell.exceptions import TcpTimeoutException
import time
import re
import json
import random
import subprocess
import psutil
import threading
import xml.etree.ElementTree as et

from proc import process as pro

PLAYER_PATH = r"C:\Program Files\BlueStacks_nxt\HD-Player.exe --instance Tiramisu64"
BLUESTACKS_CONFIG_PATH = r"C:\ProgramData\BlueStacks_nxt\bluestacks.conf"
PACK_NAME = "com.elnimrstudios.carzzle"
PROCNAME  = "HD-Player.exe"
device = None  
int_ad_status = None 

def connect(host="localhost", port=5555, max_retries=3):
    d = AdbDeviceTcp(host, port)
    for attempt in range(max_retries):
        try:
            d.connect()
            if d.available:
                #print(f"[+] ADB Connected (Attempt {attempt+1})")
                return d
        except Exception as e:
            print(f"[-] ADB Connection failed (Attempt {attempt+1}): {e}")
        time.sleep(3)
    
    print("[-] ADB Failed to connect after multiple attempts.")
    return None

def start_proc(path = PLAYER_PATH):
    try:
        subprocess.Popen(path)
        return True 
    except Exception as e:
        print(f"[-] start_proc : {e}")
        return False
    
def is_proc_running(proc_name = PROCNAME ):
    for proc in psutil.process_iter(attrs=['pid', 'name']):
        if proc_name in proc.info['name']:
            return True
    return False

def is_app_installed(package_name):
    try:
        dv = connect()
    except Exception as e :
        print(f"[-] launch_app ADB connection faild, {e}") 
        return 
    try:
        output = dv.shell("pm list packages")
        installed_packages = output.split("\n")
        return any(f"package:{package_name}" in pkg for pkg in installed_packages)
    except Exception as e:
        print(f"[-] is_app_installed Error: {e}")
        dv.close
        return False
    
def launch_app(package_name = PACK_NAME):
    try:
        dv = connect()
    except Exception as e :
        print(f"[-] launch_app ADB connection faild, {e}") 
        return 
    try:
        dv.shell(f"monkey -p {package_name} -c android.intent.category.LAUNCHER 1")
        print(f"[+] Launched {package_name} successfully!")
    except Exception as e:
        print(f"[-] ADB Failed to launch {package_name}: {e}")
    dv.close 

def is_app_running(package_name = PACK_NAME):
    try:
        dv = connect()
    except Exception as e :
        print(f"[-] is_app_running ADB connection faild, {e}") 
        return 
    try:
        output = dv.shell(f"pidof {package_name}")  # Get process ID
        return bool(output.strip())  # If output is not empty, the app is running
    except Exception as e:
        print(f"[-] Error checking if app is running: {e}")
        return False

def random_time(a, threshold=1):
    return random.uniform(a - threshold, a + threshold)


def Click(x,y,threshold = 10):
    global device 
    if not device:
        print(f"[-][Click] ADB connection failed.")
        return
    randomized_x = random.uniform( x - threshold, x + threshold  )
    randomized_y = random.uniform( y - threshold, y + threshold  )
    device.shell( f"input tap { randomized_x } { randomized_y }" )
    print(f"[+][Click] Click performed at position ({randomized_x}, {randomized_y})") 


def process_unity_log(data):
    try :
        event_type = data.get("event") or data.get("eventType")
        
        if event_type == "GameStart":
            print(f"[+] Game Started at {data.get('timestamp')}")
        
        if event_type == "PlayNow":
            print(f"[+] Play Game at {data.get('timestamp')}")
            time.sleep(1)
            pos = data.get("playbtn") 
            Click(pos['x'],pos['y'],10) 

        if event_type == "Positions":
            for pos in data.get("positionsList", []):
                time.sleep( random_time( 1.5 , 1 ) ) 
                Click(pos['x'],pos['y'],10) 


        if event_type == "PuzzleComplete":
            time.sleep( random_time( 3 , 1 ) ) 
            pos = data.get("nextlevelbtn") 
            Click(pos['x'],pos['y'],10) 
        
        if event_type == "Interstitial":
            print("[+] Interstitial Event")
        
        
        if event_type == "Rewarded":
            print("[+] Rewarded Event")
        
    except Exception as e :
        print(f"[-] Error Processing Data: {e}")
        return False

def stream_unity_logs():
    try:
        for line in device.streaming_shell("logcat -v time", read_timeout_s=10):
            if "[CARZZLE]" in line:
                clean_line = line.strip()
                print("[LOG]", clean_line)
                
                # Extract JSON part after [CARZZLE]
                match = re.search(r'\[CARZZLE\]\s+(.*)', clean_line)
                if match:
                    json_part = match.group(1)
                    try:
                        data = json.loads(json_part)
                        process_unity_log(data)
                    except json.JSONDecodeError:
                        print("[!] JSON parse error:", json_part)
    except TcpTimeoutException:
        print("[!] Timeout waiting for Unity log. Reconnecting...")
        time.sleep(2)
        stream_unity_logs()


def bounds_center(bounds):
    match = re.search(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", bounds)
    if match:
        x1, y1, x2, y2 = map(int, match.groups())
        x_center = (x1 + x2) // 2
        y_center = (y1 + y2) // 2 
        return x_center, y_center
    else:
        print("Invalid bounds format!")
        return None


def play_thread(data): 
    print("Inside play_thread ")
    try:
        dv = connect()
    except Exception as e :
        print(f"[-] play_thread ADB connection faild, {e}") 
        return 
    try:
        time.sleep( random_time( 3 , 1 ) ) 
        pos = data.get("playbtn") 
        randomized_x = random.uniform( pos['x'] - 10, pos['x'] + 10  )
        randomized_y = random.uniform( pos['y'] - 10, pos['y'] + 10  )
        dv.shell( f"input tap { randomized_x } { randomized_y }" )
    except Exception as e : 
        print("[play_thread]" , e) 
    dv.close 
     


def level_complete_thread(data):
    print("Inside level_complete_thread ")
    try:
        dv = connect()
    except Exception as e :
        print(f"[-] level_complete thread ADB connection faild, {e}") 
        return 
    try :
        time.sleep( random_time( 3 , 1 ) ) 
        pos = data.get("nextlevelbtn") 
        randomized_x = random.uniform( pos['x'] - 10, pos['x'] + 10  )
        randomized_y = random.uniform( pos['y'] - 10, pos['y'] + 10  )
        dv.shell( f"input tap { randomized_x } { randomized_y }" )
    except Exception as e : 
        print("[level_complete_thread]" , e) 
    dv.close 
     

def position_thread(data):
    print("Inside position_thread ")
    try:
        dv = connect()
    except Exception as e :
        print(f"[-] position thread ADB connection faild, {e}") 
        return 
    try :
        for pos in data.get("positionsList", []):
            time.sleep( random_time( 0.6 , 0 ) ) 
            randomized_x = random.uniform( pos['x'] - 10, pos['x'] + 10  )
            randomized_y = random.uniform( pos['y'] - 10, pos['y'] + 10  )
            print(f"[+] Perform Click on piece  {pos['name']} , at ({randomized_x}, {randomized_y})") 
            dv.shell( f"input tap { randomized_x } { randomized_y }" )  
    except Exception as e :
        print("[position_thread]" , e) 
    dv.close 
     


def handle_Interstitial_ad(data):
    print("Inside Thread Interstial Ad ")
    try:
        dv = connect()
    except Exception as e :
        print(f"[-] handle_Interstitial_ad Thread ADB connection faild, {e}") 
        return 
    try :

        while True :

            try:
                dv.shell("uiautomator dump /sdcard/ui.xml")
                time.sleep(1)
                dv.pull("/sdcard/ui.xml", "ui.xml")
                time.sleep(1)
                tree = et.parse("ui.xml") 
                root = tree.getroot()
                install = close = False 
                install_b = close_b = "[0,0][0,0]"

                for node in root.iter("node") :
                    if node.attrib.get("text")  == "Install" : 
                        install  = True 
                        install_b = node.attrib.get("bounds")
                    if node.attrib.get("text")  == "Close" : 
                        close  = True
                        close_b = node.attrib.get("bounds")

                if close : 
                    x,y = bounds_center(close_b)
                    print(f"[+] close button found at pos {x},{y}, waiting 5s")
                    time.sleep(5)
                    
                    randomized_x = random.uniform( x - 10, x + 10  )
                    randomized_y = random.uniform( y - 10, y + 10  )
                    print(f"[+] Try to close at pos {randomized_x},{randomized_y}")
                    dv.shell( f"input tap { randomized_x } { randomized_y }" )
                    print(f"[+] Tap Send at pos {randomized_x},{randomized_y}")
                    break

            except Exception as e:
                print("[-] handle_Interstitial_ad ui read error:" , e) 
            
            time.sleep(1)

    except Exception as e : 
        print("[-] handle_Interstitial_ad Loop error:" , e) 
    dv.close 
     

def start_thread(_target,_args,_daemon=True):
    thread  = threading.Thread(
        target=_target,
        args=(_args,),  # pass parameters here
        daemon=_daemon
        )
    thread.start()

def handle_data(data):
    event_type = data.get("event") or data.get("eventType")                                            
    if event_type == "GameStart":
        print("[+] GameStart Event")
    elif event_type == "PlayNow":
        print("[+] PlayNow Event")
        start_thread(play_thread,data)
    elif event_type == "Shuffling":
        print("[+] Shuffling Event")
    elif event_type == "ShuffleComplete":
        print("[+] Shuffle Complete Event")
    elif event_type == "Positions":
        print("[+] Positions Event")
        start_thread(position_thread,data)
    elif event_type == "PuzzleComplete":
        print("[+] PuzzleComplete Event")
        start_thread(level_complete_thread,data)
    elif event_type == "Interstitial":
        print("[+] Interstitial Event")
        state = data.get("message")  
        if state == "ShowingInterstitialAd" :
            print("[+][+] Showing Interstitial Ad ...")
            start_thread(handle_Interstitial_ad,data)
        elif state == "LoadingAd" :
            print("[+][+] Loading Ad ...")
        elif state == "AdLoaded" :
            print("[+][+] Ad Loaded ...")
        elif state == "AdStarted" :
            print("[+][+] Ad Started ...")
        elif state == "AdCompleted":
            int_ad_status = "AdCompleted"
            print("[+][+] Ad Completed ...")
        elif state == "AdSkipped": 
            print("[+][+] Ad Skipped")
        elif state == "AdClicked":
            print("[+][+] AdClicked")
        elif state == "InitializationNotReady":
            print("[-][-] Initialization Not Ready")
        elif state == "ShowAdFailed": 
            print("[-][-] Show Ad Failed")
        elif state == "FailedToLoadAd": 
            print("[-][-] Failed To Load Ad")
        elif state == "RetryingLoad": 
            print("[-][-] Retrying Load Ad")
        elif state == "RetryingLoadMaxRetriesReached": 
            print("[-][-] Retrying Load Max Retries Reached")           
        elif state == "AdNotReadyYet": 
            print("[-][-] Ad No Ready Yet")
        elif state == "AdNotReadyYet": 
            print("[-][-] Ad No Ready Yet")
    elif event_type == "Rewarded":
            print("[+] Rewarded Event")
    else:
        print("[+] Unknown Event")




def main_logic() :
    global device 
    while True:
        if pro.is_process_running(PROCNAME) :  
            if device :
                if is_app_running() :
                    try:
                        try:
                            device.shell("logcat -c")

                            for line in device.streaming_shell("logcat", read_timeout_s=30):
                                if "[CARZZLE]" in line:
                                    clean_line = line.strip()

                                    match = re.search(r'\[CARZZLE\]\s+(.*)', clean_line)
                                    
                                    if match:
                                        json_part = match.group(1)

                                        try:
                                            data = json.loads(json_part)
                                            handle_data(data) 

                                        except json.JSONDecodeError:
                                            print("[!] JSON parse error:", json_part)
                        except Exception as e :
                            print("[!] Connection Closed ADB log. Reconnecting...")

                    except TcpTimeoutException:
                        print("[!] Timeout waiting for Unity log. Reconnecting...")

                else: 
                    launch_app()           
            else :
                device = connect() 
                time.sleep(1)
        else:
            pro.start_proc(path=PLAYER_PATH)
            time.sleep(30)

        time.sleep(1)


if __name__ == "__main__": 
    main_logic() 