import threading
import time

class ThreadManager:
    def __init__(self, target, *args, **kwargs):
        self.target = target
        self.args = args
        self.kwargs = kwargs

        self.thread = None
        self._pause_event = threading.Event()
        self._stop_event = threading.Event()
        self._pause_event.set()  # Initially not paused

    def _run(self):
        while not self._stop_event.is_set():
            self._pause_event.wait()  # Block here if paused

            # You can insert logic here before calling the target
            self.target(*self.args, **self.kwargs)
            
            # Optional sleep if the task is fast (avoid CPU overuse)
            time.sleep(0.1)

    def start(self):
        if self.thread is None or not self.thread.is_alive():
            self._stop_event.clear()
            self._pause_event.set()
            self.thread = threading.Thread(target=self._run, daemon=True)
            self.thread.start()
            print("[ThreadManager] Thread started.")

    def pause(self):
        self._pause_event.clear()
        print("[ThreadManager] Thread paused.")

    def resume(self):
        self._pause_event.set()
        print("[ThreadManager] Thread resumed.")

    def stop(self):
        self._stop_event.set()
        self._pause_event.set()  # In case it's paused
        if self.thread:
            self.thread.join()
        print("[ThreadManager] Thread stopped.")
