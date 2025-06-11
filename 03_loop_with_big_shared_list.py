import threading
import random
import time
from math import sqrt

def distance2(a, b):
    return (a[0]-b[0])**2 + (a[1]-b[1])**2 + (a[2]-b[2])**2


def find_closest_worker(points, query_point, start, end, shared_result, lock, tid):
    local_min_dist = float("inf")
    local_min_idx = -1

    for i in range(start, end):
        d = distance2(points[i], query_point)
        if d < local_min_dist:
            local_min_dist = d
            local_min_idx = i

    with lock:
        if local_min_dist < shared_result['min_dist']:
            shared_result['min_dist'] = local_min_dist
            shared_result['closest_idx'] = local_min_idx
            shared_result['owner'] = tid


def threaded_closest_point(points, query_point, num_threads=4):
    n = len(points)
    chunk_size = n // num_threads

    shared_result = {
        'min_dist': float("inf"),
        'closest_idx': -1,
        'owner': -1
    }
    lock = threading.Lock()
    threads = []

    for tid in range(num_threads):
        start = tid * chunk_size
        end = (tid + 1) * chunk_size if tid < num_threads - 1 else n
        t = threading.Thread(target=find_closest_worker,
                             args=(points, query_point, start, end, shared_result, lock, tid))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    return shared_result['closest_idx'], sqrt(shared_result['min_dist']), shared_result['owner']

if __name__ == "__main__":
    N = 10_000_000
    num_threads = 4
    points = [[random.random(), random.random(), random.random()] for _ in range(N)]
    query_point = [random.random(), random.random(), random.random()]

    print(f"Launching threaded NN search with {num_threads} threads")
    t0 = time.time()
    idx, dist, owner = threaded_closest_point(points, query_point, num_threads)
    t1 = time.time()

    print(f"    Elapsed time: {t1 - t0:.2f} seconds")
