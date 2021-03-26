#!/bin/bash

# Capturing expected total number of worker nodes (input arguments)
STITCH_IMG_ID=$1
BROWSER=$2
HOST=$3
PORT=$4

# Verify input
## check BROWSER
if [ -z "$BROWSER" ]
then
      echo "\$BROWSER is empty"
      BROWSER="google-chrome"  # defaule value; alternative value: `firefox`
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

# setup URL
URL="http://${HOST}:8888/webview/${STITCH_IMG_ID}"

# open image in browser
${BROWSER} "${URL}"
