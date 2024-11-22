#!/bin/bash

# Load environment variables first
export $(cat .env | xargs)

# Start Gunicorn with environment variables
gunicorn --bind 0.0.0.0:${LF_API_PORT} --workers 2 --threads 4 --timeout 180 run:laserfocus