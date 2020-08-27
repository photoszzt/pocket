#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

ln -sf $SCRIPT_DIR/../client/build/client/libcppcrail.so $SCRIPT_DIR
ln -sf $SCRIPT_DIR/../client/build/pocket/libpocket.so $SCRIPT_DIR
ln -sf $SCRIPT_DIR/../client/pocket_api.py $SCRIPT_DIR
