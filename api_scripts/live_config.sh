curl --location --request PUT 'http://localhost:8888/stitching/config' \
--header 'Content-Type: application/json' \
--data-raw '{
    "processor_status": true,
    "stitching_mode": 2,

    "target_stitch": 6,

    "frame_skip": 1,
    "max_frames": 4
}'
echo ""
