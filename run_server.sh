#!/bin/bash
cd backend
# Add project root to PYTHONPATH so 'agent' module can be imported
export PYTHONPATH=$PYTHONPATH:$(pwd)/..
# Default to port 8005
PORT=${PORT:-8005}
PORT=$PORT uv run python ../agent/server.py
