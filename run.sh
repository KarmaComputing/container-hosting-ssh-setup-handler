#!/bin/bash

# Note must be ran as dokku user or a user with (sudoers) permissions to edit
# the file /home/dokku/.ssh/authorized_keys
FLASK_ENV=development flask run --host 0.0.0.0
