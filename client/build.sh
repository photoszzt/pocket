#!/bin/bash
sudo apt-get install -y cmake libboost-all-dev python-dev python3-dev
mkdir -p build
cd build
cmake ..
make
