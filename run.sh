#!/bin/bash

# Load environment variables first
export $(cat .env | xargs)

# Start Gunicorn with environment variables
gunicorn --bind 0.0.0.0:${LF_API_PORT} --timeout 180 run:laserfocus