
# 🚀 Benchmarks de Python 3.14b2 avec `--disable-gil`

## 🧠 Un peu de contexte : le GIL, pourquoi et pour quoi faire ?

Le GIL (*Global Interpreter Lock*) est un mécanisme présent dans l’implémentation CPython depuis toujours. Il garantit qu’un seul et unique thread peut exécuter du bytecode Python à la fois. Ce mécanisme permet historiquement de grandement simplifier la gestion de la mémoire interne de l’interpréteur.

Néanmoins, ce verrou global a un effet de bord majeur : **les programmes multi-threads ne scalent pas sur plusieurs cœurs** pour des workloads *CPU-bound*.

➡️ En pratique, `threading.Thread` est donc surtout utilisé pour des I/O. 

Depuis des années, la suppression du GIL était un sujet récurrent dans la communauté Python. Depuis Python 3.13, ça se concrétise !

## 🧪 Python 3.13 introduit un mode expérimental : `--disable-gil`

C’est l’objet de la [PEP 703 – Making the Global Interpreter Lock Optional](https://peps.python.org/pep-0703/) proposée par Sam Gross, qui a fait beaucoup parler d’elle. Depuis Python 3.13, il est possible de permettre la désactivation du GIL — pour cela, il faut que l'interpréteur Python soit compilé avec l'option `--disable-gil`.

Avec ce mode activé à la compilation, le GIL est pilotable via la variable d'environnement `PYTHON_GIL=0|1`. 

Par exemple, pour lancer un script en mode `nogil`, il suffit de faire : 

```bash
PYTHON_GIL=0 python3 my_script.py
```

Quelques benchmarks existent en ligne, par exemple [celui-ci](https://medium.com/@r_bilan/python-3-13-without-the-gil-a-game-changer-for-concurrency-5e035500f0da). Mais j’ai voulu approfondir un peu le sujet et évaluer l'apport potentiel de cette révolution !

## 🔧 Setup pour les tests 

Pour faire mes tests, j’ai mis en place une image Docker qui compile Python 3.14b2 avec l'option `--disable-gil`. Le Dockerfile et l’ensemble des cas de test sont disponibles [ici](...).

Pour construire le Docker :

```
$ docker build . -f Dockerfile-nogil -t python:nogil_3.14b2
``` 

## ⚙️ Benchmark #1 : Factorielle lourde en multi-thread

Pour le premier test, on fait tout bêtement un gros calcul de factorielle dans plusieurs threads.

```python
import threading
import math
import time 

def test_function(num_thread):
    thread_start_time = time.time()
    math.factorial(250000)
    thread_execution_time = time.time() - thread_start_time

start_time = time.time()

threads = []
for num_thread in range(5):
    thread = threading.Thread(target=test_function, args=(num_thread,))
    thread.start()
    threads.append(thread)

for thread in threads:
    thread.join()

execution_time = time.time() - start_time
print(f"     Elapsed time: {execution_time:.2f} seconds")
```

### 🧾 Résultats

| Mode         | Temps total |
|--------------|-------------|
| GIL ON       | 1.97 s      |
| GIL OFF      | 0.56 s      |

✅ **Gain ×3~4** : ici, `--disable-gil` permet une vraie parallélisation du calcul lourd avec un très bon scaling.

## ⚙️ Benchmark #2 : Calculs mathématiques modérés

Même idée que précédemment, mais avec une charge mathématique un peu plus variée.

```python
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
```

### 🧾 Résultats

| Mode         | Temps total |
|--------------|-------------|
| GIL ON       | 1.36 s      |
| GIL OFF      | 0.41 s      |

✅ **Gain ×3~4 à nouveau**, scaling constant.

## ⚙️ Benchmark #3 : Accès concurrent partagé

On ajoute ici des écritures dans une variable partagée (une liste Python). Chaque thread écrit dans une case distincte.

```python
def stress_function(thread_id, complexity, shared_data, lock):
    local_result = 0.0
    for i in range(1, complexity):
        a = math.sqrt(i) + math.sin(i) ** 2
        b = math.log1p(i) * math.exp(-a)
        c = math.factorial(i % 500 + 500) % 10**8
        local_result += a * b + c
    shared_data[thread_id] = local_result

def run_threads(num_threads=4, complexity=10_000):
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
    print(f"     Elapsed time: {total_time:.2f} seconds")
    print(f"        -> Global result: {total_sum % 1000:.2f}")
```

### 🧾 Résultats

| Mode         | Temps total |
|--------------|-------------|
| GIL ON       | 1.32 s      |
| GIL OFF      | 0.43 s      |

🔒 Grâce à un découpage propre 😎 (pas de collision entre threads), `nogil` reste très efficace ici.

## ⚠️ Benchmark #4 : Recherche du plus proche voisin sur 10M points

Test plus réaliste : 10M de points 3D aléatoires, recherche du plus proche voisin en multithreading avec dictionnaire partagé.

```python
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
```

### 🧾 Résultats

| Mode         | Temps total |
|--------------|-------------|
| GIL ON       | 2.38 s      |
| GIL OFF      | 3.61 s ❗    |

❌ Et là, grosse surprise : activer `nogil` rend les choses plus lentes. Je n'ai pas vraiment d'explication certaine. Mais si je devais avancer une théorie je dirais que l'accès concurrent à la grosse liste Python entraine quelques limitations. 

## 🔁 Bonus : version C++ équivalente + `nanobind`

J’ai aussi testé ce cas en C++ multithreadé natif, exposé à Python via [`nanobind`](https://github.com/wjakob/nanobind). c'est surtout pour voir si en suivant exactement la même logique mais en changeant juste la stack technique on obtient des résultats différents. Et donc oui : 

| Implémentation      | Temps total |
|---------------------|-------------|
| Python GIL ON       | 2.38 s      |
| Python GIL OFF      | 3.61 s ❗    |
| C++ (threads)       | 0.88 s ✅    |

En version threads c++ on a bien un gros gain de performance. Donc la logique est bonne, pas trop mauvaise en tout cas, la limitation vient de Python 😿. 

## 🔚 Conclusion

Python progresse — c’est indéniable et enthousiasmant. Mais pour des cas fortement concurrentiels, les implémentations natives (C/C++) gardent un net avantage.


- ✅ Python 3.14 `--disable-gil` **offre des gains réels** pour des tâches *CPU-bound* multithreadées
- ⚠️ Mais les performances **ne sont pas systématiquement meilleures**, notamment dès qu’il y a de gros volumes de données ou de la contention mémoire

## 📚 Pour aller plus loin

- [PEP 703 — Making the Global Interpreter Lock Optional](https://peps.python.org/pep-0703/)
- [Python 3.14 changelog (beta)](https://docs.python.org/3.14/whatsnew/3.14.html)
- [nanobind GitHub](https://github.com/wjakob/nanobind)