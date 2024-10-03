#!/bin/bash

# Open a new terminal window and run python run.py
gnome-terminal -- bash -c "gunicorn --config gunicorn.conf.py run:application; exec bash"

# Open another terminal window and run sudo caddy run
gnome-terminal -- bash -c "caddy run; exec bash"

# Keep the script running
wait
