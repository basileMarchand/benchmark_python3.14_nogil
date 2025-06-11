#include <nanobind/nanobind.h>
#include <nanobind/stl/vector.h>
#include <nanobind/stl/tuple.h>
#include <cmath>
#include <limits>
#include <thread>
#include <mutex>

namespace nb = nanobind;
using namespace nb::literals;

using Point = std::vector<double>;

struct Result {
    double min_dist = std::numeric_limits<double>::max();
    int idx = -1;
    int owner = -1;
};

double distance2(const Point& a, const Point& b) {
    return (a[0]-b[0]) * (a[0]-b[0])
         + (a[1]-b[1]) * (a[1]-b[1])
         + (a[2]-b[2]) * (a[2]-b[2]);
}

void worker(const std::vector<Point>& points,
            const Point& query,
            int start, int end,
            Result& shared_result,
            std::mutex& mtx,
            int tid) {

    double local_min = std::numeric_limits<double>::max();
    int local_idx = -1;

    for (int i = start; i < end; ++i) {
        double d2 = distance2(points[i], query);
        if (d2 < local_min) {
            local_min = d2;
            local_idx = i;
        }
    }

    std::lock_guard<std::mutex> lock(mtx);
    if (local_min < shared_result.min_dist) {
        shared_result.min_dist = local_min;
        shared_result.idx = local_idx;
        shared_result.owner = tid;
    }
}

nb::tuple threaded_closest(const std::vector<Point>& points,
                           const Point& query,
                           int num_threads) {

    int n = points.size();
    int chunk_size = n / num_threads;
    Result shared_result;
    std::mutex mtx;
    std::vector<std::thread> threads;

    for (int tid = 0; tid < num_threads; ++tid) {
        int start = tid * chunk_size;
        int end = (tid == num_threads - 1) ? n : (tid + 1) * chunk_size;
        threads.emplace_back([&points, &query, &mtx, &shared_result, start, end, tid]() {
             double local_min = std::numeric_limits<double>::max();
            int local_idx = -1;

            for (int i = start; i < end; ++i) {
                double d2 = distance2(points[i], query);
                if (d2 < local_min) {
                    local_min = d2;
                    local_idx = i;
                }
            }

            std::lock_guard<std::mutex> lock(mtx);
            if (local_min < shared_result.min_dist) {
                shared_result.min_dist = local_min;
                shared_result.idx = local_idx;
                shared_result.owner = tid;
            }
        });
    }
    for (auto& t : threads)
        t.join();

    return nb::make_tuple(shared_result.idx,
                        std::sqrt(shared_result.min_dist),
                        shared_result.owner);
    }



NB_MODULE(nearest_cpp, m) {
    m.def("threaded_closest", &threaded_closest,
          "points"_a, "query_point"_a, "num_threads"_a);
}
