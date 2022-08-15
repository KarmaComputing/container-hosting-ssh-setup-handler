#!/bin/bash

# Note must be ran as dokku user or a user with (sudoers) permissions to edit
# the file /home/dokku/.ssh/authorized_keys
FLASK_DEBUG=1 flask run --host 0.0.0.0
