#!/bin/bash

if [ $# -eq 0 ]; then
  echo "Usage: $0 <command> [arg1 arg2 ...]"
  exit 1
fi

COMMAND="$1"

source .env

shift

"$COMMAND" "$@"
