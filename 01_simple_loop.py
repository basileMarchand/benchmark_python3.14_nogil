import threading
import math
import time
import random

def stress_function(thread_id, complexity):
    result = 0
    for i in range(1, complexity):
        a = math.sqrt(i) + math.sin(i) ** 2
        b = math.log1p(i) * math.exp(-a)
        c = math.factorial(i % 500 + 500) % 10**8  # borné pour ne pas exploser la RAM
        result += a * b + c

def run_threads(num_threads=4, complexity=10_000):
    print(f"Launching {num_threads} threads with complexity {complexity}")
    threads = []

    start_time = time.time()
    for i in range(num_threads):
        t = threading.Thread(target=stress_function, args=(i, complexity))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()
    total_time = time.time() - start_time
    print(f"   Elapsed time {total_time:.2f} seconds")

if __name__ == "__main__":
    run_threads(num_threads=5, complexity=20_000)
