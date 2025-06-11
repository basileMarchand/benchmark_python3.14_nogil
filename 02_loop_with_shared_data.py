import threading
import math
import time

def stress_function(thread_id, complexity, shared_data, lock):

    local_result = 0.0
    for i in range(1, complexity):
        a = math.sqrt(i) + math.sin(i) ** 2
        b = math.log1p(i) * math.exp(-a)
        c = math.factorial(i % 500 + 500) % 10**8
        local_result += a * b + c

    shared_data[thread_id] = local_result

def run_threads(num_threads=4, complexity=10_000):
    print(f"Launching {num_threads} threads with complexity {complexity}")
    threads = []
    shared_data = [0.0] * num_threads
    lock = threading.Lock()

    start_time = time.time()
    for i in range(num_threads):
        t = threading.Thread(target=stress_function, args=(i, complexity, shared_data, lock))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    total_time = time.time() - start_time
    total_sum = sum(shared_data)
    print(f"     Elasped time {total_time:.2f} seconds")
    print(f"        -> Global result: {total_sum % 1000:.2f}")

if __name__ == "__main__":
    run_threads(num_threads=5, complexity=20_000)
