import nearest_cpp
import random
import time

N = 10_000_000
T = 4
points = [[random.random(), random.random(), random.random()] for _ in range(N)]
query = [random.random(), random.random(), random.random()]

print(f"Running C++ wrapped nearest neighbor with {T} threads...")
t0 = time.time()
idx, dist, owner = nearest_cpp.threaded_closest(points, query, T)
t1 = time.time()
print(f"    Elapsed time: {t1 - t0:.2f} seconds")
