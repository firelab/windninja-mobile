#!/bin/bash

# Workaround to load system environment variables
# into the shell for supervisor subprocesses
# https://github.com/Supervisor/supervisor/issues/242

ENV_FILE="$1"
CMD=${@:2}

set -o allexport
source $ENV_FILE
set +o allexport

$CMD
