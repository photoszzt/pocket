#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cp $SCRIPT_DIR/../client/build/client/libcppcrail.so $SCRIPT_DIR
cp $SCRIPT_DIR/../client/build/pocket/libpocket.so $SCRIPT_DIR
cp $SCRIPT_DIR/../client/pocket.py $SCRIPT_DIR
