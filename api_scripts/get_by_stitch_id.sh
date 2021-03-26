#!/bin/bash

# Capturing expected total number of worker nodes (input arguments)
STITCH_IMG_ID=$1
TO_URL=$2
HOST=$3
PORT=$4

# Verify input
## check STITCH_IMG_ID
if [ -z "$STITCH_IMG_ID" ]
then
      echo "\$STITCH_IMG_ID is empty"
fi

## check TO_URL
if [ -z "$TO_URL" ]
then
      echo "\$TO_URL is empty"
      TO_URL="true"  # default value
fi

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

curl --location --request GET "http://${HOST}:8888/stitching/${STITCH_IMG_ID}?to_url=${TO_URL}"
echo ""
