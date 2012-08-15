#!/bin/bash
parentdir=${0%/*}
cd "$parentdir"
./python/bin/python builder.py
