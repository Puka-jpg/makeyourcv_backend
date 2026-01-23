#!/bin/bash
cd backend
export PYTHONPATH=$PYTHONPATH:$(pwd)/..
uv run ../agent/main.py
