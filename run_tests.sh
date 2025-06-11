#!/bin/bash

# This script runs the tests for the project (factorized version).

declare -a scripts=(
  "00_simple_factorial.py"
  "01_simple_loop.py"
  "02_loop_with_shared_data.py"
  "03_loop_with_big_shared_list.py"
)

for script in "${scripts[@]}"; do
  base="${script%%.*}"
  echo "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
  echo "++++ Running $base in with GIL enabled"
  PYTHON_GIL=1 python3 "$script"
  echo "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
  echo "++++ Running $base in with GIL disabled"
  PYTHON_GIL=0 python3 "$script"
done

echo "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
echo "++++ Running 03b with nanobind plugin "
PYTHON_GIL=0 python3 03b_loop_with_big_shared_list_nanobind.py  