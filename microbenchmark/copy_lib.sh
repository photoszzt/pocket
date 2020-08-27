#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

cp $SCRIPT_DIR/../client/build/client/libcppcrail.so $SCRIPT_DIR
cp $SCRIPT_DIR/../client/build/pocket/libpocket.so $SCRIPT_DIR
cp $SCRIPT_DIR/../client/pocket_api.py $SCRIPT_DIR
cp /usr/lib/x86_64-linux-gnu/libboost_python3-py36.so.* $SCRIPT_DIR
cp /lib/x86_64-linux-gnu/libc.so.6 $SCRIPT_DIR
cp /usr/lib/x86_64-linux-gnu/libstdc++.so.6 $SCRIPT_DIR
