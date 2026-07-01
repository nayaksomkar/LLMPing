#!/bin/sh
if [ $# -eq 0 ]; then
    python server.py
else
    python main.py "$@"
fi
