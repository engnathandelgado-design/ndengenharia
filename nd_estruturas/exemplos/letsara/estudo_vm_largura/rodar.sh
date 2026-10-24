#!/bin/bash
# roda as configs passadas, 2 em paralelo
run(){ python3 ../mef_vm_largura_1f.py "$1" > "${1%.json}_1f.log" 2>&1; }
export -f run
printf "%s\n" "$@" | xargs -P 2 -I{} bash -c 'run {}'
