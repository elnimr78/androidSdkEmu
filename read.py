from adb_shell.adb_device import AdbDeviceTcp
from adb_shell.exceptions import TcpTimeoutException
import time

import xml.etree.ElementTree as et

def read_ui():
    try:
        dv = AdbDeviceTcp("localhost", 5555)
        dv.connect()
    except Exception as e :
        print("[-] Connection Error" , e) 
        return 
    try :
        dv.shell("uiautomator dump /sdcard/ui.xml")
        time.sleep(1)
        dv.pull("/sdcard/ui.xml", "ui.xml")
        time.sleep(0.5)
        tree = et.parse("ui.xml")  
        root = tree.getroot()
        print("[+] Read Success") 
        
    except Exception as e : 
        print("[-] Read error" , e) 
    dv.close 



def handle_Interstitial_ad(data):
    print("Inside Thread Interstial Ad ")
    try:
        dv = AdbDeviceTcp("localhost", 5555)
        dv.connect()
    except Exception as e :
        print("[handle_Interstitial_ad]" , e) 
        return 
    try :

        while True :

            dv.shell("uiautomator dump /sdcard/ui.xml")
            time.sleep(0.5)
            dv.pull("/sdcard/ui.xml", "ui.xml")
            time.sleep(0.5)
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
                #print("install>",install," close>",close)

            if close : 
                x,y = bounds_center(close_b)
                randomized_x = random.uniform( x - 10, y + 10  )
                randomized_y = random.uniform( x - 10, y + 10  )
                dv.shell( f"input tap { randomized_x } { randomized_y }" )
                print("Existing Inter. Ad .. ") 
                break
        
            time.sleep(1)

    except Exception as e : 
        print("[level_complete_thread]" , e) 
    dv.close 

read_ui()