#!/bin/bash

# Capturing expected total number of worker nodes (input arguments)
TO_URL=$1
HOST=$2
PORT=$3

# Verify input
## check TO_URL
if [ -z "$TO_URL" ]
then
      echo "\$TO_URL is empty"
      TO_URL="true"  # default value
fi
echo "\$TO_URL = ${TO_URL}"


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

curl --location --request GET "http://${HOST}:8888/stitching?to_url=${TO_URL}"
echo ""
