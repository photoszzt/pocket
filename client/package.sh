#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
sudo mkdir -p /var/local/$USER/.faas/pocket_api
sudo cp $SCRIPT_DIR/build/client/libcppcrail.so \
    $SCRIPT_DIR/build/pocket/libpocket.so \
    $SCRIPT_DIR/pocket_api.py \
    /usr/lib/x86_64-linux-gnu/libboost_python3-py36.so.* \
    /var/local/$USER/.faas/pocket_api
