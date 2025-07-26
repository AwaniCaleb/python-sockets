import time
import threading

class Intervals:
    def __init__(self):
        # A dictionary to store active threads and their stop events.
        # Using use a WeakValueDictionary to automatically remove entries
        # if the thread object itself is no longer referenced elsewhere.
        # However, for the stop_event, we need to ensure it stays alive
        # as long as the thread is running. So, a regular dict with
        # Thread and Event objects is generally safer here.
        # We'll use a regular dict and explicitly remove entries on stop.
        self._active_intervals: dict[str, tuple[threading.Thread, threading.Event]] = {}
        self._lock = threading.Lock() # For thread-safe access to _active_intervals

    def set(self, function: callable, seconds: int) -> str:
        """
        Starts a function that runs repeatedly in a new thread.

        Args:
            function: The callable to execute.
            seconds: The interval in seconds between executions.

        Returns:
            The name of the started thread, which can be used to stop it.
        """
        if not callable(function) or not isinstance(seconds, (int, float)) or seconds <= 0:
            raise ValueError("Function must be callable and seconds must be a positive number.")

        stop_event = threading.Event()

        def wrapper():
            # Check the stop_event's flag.
            # wait(timeout) is good as it allows for periodic checks
            # without busy-waiting and can still respond quickly to a stop signal.
            while not stop_event.is_set():
                function()
                stop_event.wait(seconds) # Wait for 'seconds' or until the event is set
            print(f"Thread '{threading.current_thread().name}' stopping.")

        thread = threading.Thread(target=wrapper, daemon=True)
        # Give the thread a more descriptive name if possible
        thread.name = f"IntervalThread-{function.__name__}-{int(time.time())}"

        with self._lock:
            # Store the thread and its stop event
            self._active_intervals[thread.name] = (thread, stop_event)
        
        thread.start()
        print(f"Started interval thread: {thread.name}")
        return thread.name

    def stop(self, name: str) -> bool:
        """
        Stops a running interval thread by its name.

        Args:
            name: The name of the thread to stop.

        Returns:
            True if the thread was found and a stop signal was sent, False otherwise.
        """
        thread_info = None
        with self._lock:
            thread_info = self._active_intervals.pop(name, None)

        if thread_info:
            thread, stop_event = thread_info
            stop_event.set() # Signal the thread to stop
            
            # Optional: Wait for the thread to finish. 
            # If it's a daemon thread, it will exit when the main program exits,
            # but joining explicitly ensures it completes its cleanup before
            # the stop() method returns. Be cautious with join() on daemon threads
            # if the main program might exit quickly, as it can block.
            # If your main program is long-running, this is fine.
            # thread.join() 
            print(f"Sent stop signal to thread: {name}")
            return True
        else:
            print(f"Thread '{name}' not found or already stopped.")
            return False

    def stop_all(self):
        """Stops all currently running interval threads."""
        threads_to_stop = []
        with self._lock:
            # Get a list of all current threads and events to stop
            threads_to_stop = list(self._active_intervals.values())
            self._active_intervals.clear() # Clear the dictionary

        for thread, stop_event in threads_to_stop:
            stop_event.set()
            # If you join, this method will block until all threads have finished.
            # thread.join()
        print("Sent stop signal to all interval threads.")
