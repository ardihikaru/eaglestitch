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

curl --location --request PUT "http://${HOST}:${PORT}/stitching/config" \
--header "Content-Type: application/json" \
--data-raw '{
    "processor_status": true,
    "stitching_mode": 2,

    "target_stitch": 6,

    "frame_skip": 1,
    "max_frames": 4
}'
echo ""
