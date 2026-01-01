#!/usr/bin/env bash
# Simple benchmark script - measure time and memory using /usr/bin/time
# Usage: ./bench.sh sample.pdf

if [ -z "$1" ]; then
  echo "Usage: $0 <pdf-file>"
  exit 1
fi

PDF="$1"
echo "Benchmarking analyze of $PDF"
/usr/bin/time -v python -m docustruct.cli analyze "$PDF" --out /tmp/out.json
echo "Output written to /tmp/out.json"
