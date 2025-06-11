import threading
import math
import time 

def test_function(num_thread):
    thread_start_time = time.time()
    math.factorial(250000)
    thread_execution_time = time.time() - thread_start_time

start_time = time.time()

# Create multiple threads
threads = []
for num_thread in range(5):
    thread = threading.Thread(target=test_function, args=(num_thread,))
    thread.start()
    threads.append(thread)

# Wait for all threads to finish
for thread in threads:
    thread.join()

execution_time = time.time() - start_time
print(f"     Elapsed time: {execution_time:.2f} seconds")