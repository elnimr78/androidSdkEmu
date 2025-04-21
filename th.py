from th_manager import ThreadManager 
import time 

def my_task():
    print("Working...", time.strftime("%H:%M:%S"))



manager = ThreadManager(my_task) 
manager.start()

time.sleep(2)
manager.pause()


time.sleep(2)
manager.resume()


time.sleep(2)
manager.stop()

while  True : 
    time.sleep(1)
