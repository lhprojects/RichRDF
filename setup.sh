#!/bin/bash

# Check if the script is being sourced
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  echo "❗ Please source this script: use 'source setup.sh' instead of running it."
  exit 1
fi

# Get the absolute path of the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if SCRIPT_DIR is already in PYTHONPATH
case ":$PYTHONPATH:" in
  *":$SCRIPT_DIR:"*)
    echo "✔ PYTHONPATH already contains: $SCRIPT_DIR"
    ;;
  *)
    export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"
    echo "✅ PYTHONPATH updated to: $PYTHONPATH"
    ;;
esac

