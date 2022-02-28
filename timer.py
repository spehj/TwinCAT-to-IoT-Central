import time

class TimerError(Exception):
    """A custom exception used to report errors in use of Timer class"""


class Timer:

    def __init__(self):
        self._start_time = None

        
        # Elapsed time in one period
        self._elapsed_time = 0
        # Total elapsed time in each state
        self._full_time = 0
        # Current total elapsed time in the state
        self._current_time = 0
    


    def start(self):

        if self._start_time is not None:
            raise TimerError(f"Timer is running. Use .stop() to stop it.")
        
        self._start_time =time.perf_counter()
        return self._start_time



    def stop(self, prejsnje_stanje):

        if self._start_time is None:
            raise TimerError(f"Timer is not running. Use a .start() to start it.")
        
        self._elapsed_time = time.perf_counter() - self._start_time
        self._full_time += self._elapsed_time
        self._start_time = None
        
        print("|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||")
        print(f" |||    Time elapsed in this period {prejsnje_stanje}: {self._elapsed_time:0.1f} seconds    |||")
        print("|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||")
        return self._current_time
        


    def current(self):
   
    
        if self._start_time is not None:
            
            self._current_time = self._full_time + (time.perf_counter() - self._start_time)
        elif self._start_time is None:
            
            self._current_time = self._full_time
            
        return self._current_time

        
    
