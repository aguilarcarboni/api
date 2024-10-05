#!/bin/bash

# Function to safely stop processes using a specific port
stop_port() {
    local port=$1
    local pids=$(lsof -ti:$port)
    if [ ! -z "$pids" ]; then
        echo "Stopping processes using port $port"
        for pid in $pids; do
            local command=$(ps -p $pid -o comm=)
            if [[ $command == *"python"* || $command == *"gunicorn"* || $command == *"caddy"* ]]; then
                echo "Stopping $command (PID: $pid)"
                kill $pid
            else
                echo "Skipping $command (PID: $pid) as it doesn't seem to be our target process"
            fi
        done
    else
        echo "No process found using port $port"
    fi
}

# Safely stop processes on specific ports
stop_port 5002  # Gunicorn port
stop_port 2019  # Caddy HTTP port
stop_port 80    # Caddy HTTP port
stop_port 443   # Caddy HTTPS port

# Wait a moment for processes to fully terminate
sleep 2

# Open a new terminal window and run gunicorn
gnome-terminal -- bash -c "gunicorn --config gunicorn.conf.py run:laserfocus; exec bash"

# Open another terminal window and run caddy
gnome-terminal -- bash -c "sudo caddy run; exec bash"

# Keep the script running
wait
