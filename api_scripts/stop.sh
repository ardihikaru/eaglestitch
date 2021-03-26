#!/bin/bash

# Capturing expected total number of worker nodes (input arguments)
HOST=$1
PORT=$2

# Verify input
## check HOST
if [ -z "$HOST" ]
then
      echo "\$HOST is empty; set value as 'localhost'"
      HOST="localhost"  # default value
fi

## check PORT
if [ -z "$PORT" ]
then
      echo "\$PORT is empty; set value as '8888'"
      PORT="8888"  # default value
fi

curl --location --request GET "http://${HOST}:${PORT}/stitching/trigger/stop"
echo ""
