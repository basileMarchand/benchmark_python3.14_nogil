
# 🐍 Python 3.14 Benchmarks with `--disable-gil`

This repository contains the source code and setup used to benchmark the experimental `--disable-gil` mode introduced in Python 3.13/3.14.

## 📦 Repository Contents

- `Dockerfile-nogil`: Dockerfile to build Python 3.14b2 with the `--disable-gil` compile option
- four multithreaded test cases used to benchmark GIL vs no-GIL performance
- `ARTICLE.md`: my notes in french for the dev.to article

## 🚀 Running the Benchmarks

```bash
docker build -f Dockerfile-nogil -t python:nogil_3.14b2 .
docker run -it python:nogil_3.14b2
```

## 📝 Related Article

The full article describing these benchmarks is available on dev.to 



## 📚 Useful References

- [PEP 703 — Making the Global Interpreter Lock Optional](https://peps.python.org/pep-0703/)
- [nanobind (C++ bindings)](https://github.com/wjakob/nanobind)
