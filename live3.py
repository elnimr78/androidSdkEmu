from adb_shell.exceptions import TcpTimeoutException
from proc import process as proc 
from adb_utils import app , device , actions , ui
import time 
import re 
import json 
import threading 
import random 
from pygame.math import Vector2 , Vector3  
from th_manager import ThreadManager 

PLAYER_PATH = r"C:\Program Files\BlueStacks_nxt\HD-Player.exe"
INSTANCE    = r" --instance Tiramisu64"
CONFIG_PATH = r"C:\ProgramData\BlueStacks_nxt\bluestacks.conf"
PACK_PATH   = r"D:\a\master\master\downloads\carzille.apk"
PACK_NAME = "com.elnimrstudios.carzzle"
PROCNAME  = "HD-Player.exe"
exit = False 

signal_start_Player = False  
signal_app_Launched = False

PERIOD_PLS_STARTING = 30
PERIOD_APP_LAUNCING = 5
PERIOD_APP_INSTALL = 10 
PERIOD_CLOSE = 7
dev = None 

is_app_running = False 
is_player_running = False 
is_player_exist  = False 
is_ShowingAd = False 

btn_shffule = Vector2(0,0) 
btn_watch = Vector2(0,0) 
btn_settings = Vector2(0,0) 

is_moves = True  


def random_time(a, threshold=1):
    return random.uniform(a - threshold, a + threshold)

def start_thread(_target,_args,_daemon=True):
    thread  = threading.Thread(
        target=_target,
        args=(_args,),  # pass parameters here
        daemon=_daemon
        )
    thread.start()

def play_thread(data): 
    print("Inside play_thread ")
    try:
        time.sleep( random_time( 3 , 1 ) ) 
        pos = data.get("playbtn") 
        actions.tap(pos['x'],pos['y'])
    except Exception as e : 
        print(f"[play_thread] exception: {e}")
     
def level_complete_thread(data):
    print("Inside level_complete_thread ")
    try :
        time.sleep( random_time( 3 , 1 ) ) 
        pos = data.get("nextlevelbtn") 
        actions.tap(pos['x'],pos['y'])
    except Exception as e : 
        print(f"[level_complete_thread] exception: {e}")
     
def position_thread(data):
    global is_moves 
    print("Inside position_thread ")
    try :
        for pos in data.get("positionsList", []):
            time.sleep( random_time( 0.6 , 0 ) ) 
            actions.tap(pos['x'],pos['y'])

            if not is_moves :
                while True :
                    if is_moves :  
                        time.sleep( random_time( 0.6 , 0 ) ) 
                        actions.tap(pos['x'],pos['y'])
                        break 
                    time.sleep(1)    
            
    except Exception as e :
        print(f"[position_thread] exception: {e}") 
     
def handle_Interstitial_ad(data):
    print("Inside Thread Interstial Ad ")
    try :
        time.sleep(1)
    except Exception as e : 
        print(f"[-] handle_Interstitial_ad Loop error: {e}") 
    
def monitor():
    global is_app_running 
    #global is_player_running 
    #global is_player_exist
    #global is_ShowingAd

    while True :
        if is_app_running:
            try:
                ui.read_ui()
                close , close_bounds = ui.find(query="Close",type="text")
                if close :
                    timeToClose = random_time(PERIOD_CLOSE,2) 
                    print(f"[+][monitoring] Ad Running closing after {timeToClose}s") 
                    time.sleep(timeToClose)
                    actions.tap(bounds=close_bounds)

            
                #else :
                    #print(f"[+][monitoring] No Close button") 
            except Exception as e:
                print(f"[-][monitoring] exception: {e}")   
        #else :
            #print(f"[-][monitoring] waiting to connect ...")

        time.sleep(1)
    
def handle_events(data):
    global btn_shffule
    global btn_settings
    global btn_watch 
    global is_moves

    event_type = data.get("event") or data.get("eventType")                                            
    if event_type   == "GameStart":
        print("[+] GameStart Event")
    elif event_type == "PlayNow":
        print("[+] PlayNow Event")
        start_thread(play_thread,data)
    elif event_type == "Shuffling":
        print("[+] Shuffling Event, setting Buttons Positions")
        pos1 = data.get("shufflebtn") 
        pos2 = data.get("watchAdbtn") 
        pos3 = data.get("settingsbtn")
        btn_shffule = Vector2(pos1["x"],pos1["y"]) 
        btn_watch  = Vector2(pos2["x"],pos1["y"])
        btn_settings = Vector2(pos3["x"],pos1["y"])   
    elif event_type == "ShuffleComplete":
        print("[+] Shuffle Complete Event")
    elif event_type == "Positions":
        print("[+] Positions Event")
        start_thread(position_thread,data)
        
    elif event_type == "PuzzleComplete":
        print("[+] PuzzleComplete Event")
        start_thread(level_complete_thread,data)
        
    elif event_type == "Interstitial" or event_type == "Rewarded" :
        print(f"[+] {event_type} Event")
        state = data.get("message")  
        if state == "ShowingInterstitialAd" :
            print("[+][+] Showing Interstitial Ad ...")
            #start_thread(handle_Interstitial_ad,data)
        elif state == "LoadingAd" :
            print("[+][+] Loading Ad ...")
        elif state == "AdLoaded" :
            print("[+][+] Ad Loaded ...")
        elif state == "AdStarted" :
            print("[+][+] Ad Started ...")
        elif state == "AdCompleted":
            int_ad_status = "AdCompleted"
            print("[+][+] Ad Completed ...")
            if not is_moves : is_moves = True  
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
    elif event_type == "Moves":
        print("[+] Moves Event")
        message = data.get("message")  
        if message == "Empty" :
            is_moves = False  
            timetowatch = random_time(3,1)
            print(f"Watching ad in {timetowatch}s")
            actions.tap(btn_watch.x,btn_watch.y)


    else:
        print(f"[-] Unkown Event type ({event_type} msg: {data.get("message")}).")




def watcher() :
    global signal_start_Player 
    global signal_app_Launched
    global exit 
    global dev 
    global is_app_running

    if not proc.is_application_exist(PLAYER_PATH) :
        print(f"[-] Player Not Found, Now Existing ... ")
        exit = True 
        return
    
    while True :

        
        if proc.is_process_running(PROCNAME):
            #print ("Player is Running ")
            signal_start_Player = False  

            if not dev :
                dev = device.connect()
                print("Try To Connect to Server ..... ")

            else:
                print("Connected ........ ")
                
                try:
                    if app.is_running(PACK_NAME) :
                        is_app_running = True 
                        signal_app_Launched = False 
                    else:
                        is_app_running = False 
                        signal_app_Launched = True  
                    
                    for line in dev.streaming_shell("logcat", read_timeout_s=30):

                        if signal_app_Launched :
                            signal_app_Launched = False  
                            is_app_running = True 
                            app.launch_app(PACK_NAME)


                        #print(line) 
                        if "[CARZZLE]" in line:
                            clean_line = line.strip()
                            match = re.search(r'\[CARZZLE\]\s+(.*)', clean_line)
                            if match:
                                json_part = match.group(1)
                                try:
                                    data = json.loads(json_part)
                                    #print(data) 
                                    handle_events(data)
                                except json.JSONDecodeError:
                                    print("[!] JSON parse error:", json_part)

                except Exception as e:
                    print(f"[!] Error :{e}")
                    print("[!] Timeout. Reconnecting...")
                    dev = None 
                    signal_app_Launched = False 
            
        else:
            if not signal_start_Player :
                print ("Player is Not Running , starting it .. ")
                signal_start_Player = True 
                proc.start_proc(PLAYER_PATH)
            else:
                print ("waiting player to starts .. ")

        time.sleep(1)


if __name__ == "__main__": 
    
    watch = threading.Thread(target=watcher,daemon=True ) 
    monit = threading.Thread(target=monitor,daemon=True )
    watch.start() 
    monit.start()

    while not exit :
        time.sleep(1)
    