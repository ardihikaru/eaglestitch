# eaglestitch
2D-ST

# Common information
- RestAPI URL: `$ http://<domain>:8888`

# Installation
- Please perform this before installing zenoh:
    ```
    $ pip install --upgrade pip
    $ pip install maturin
    ```
- Install requirements: `$ pip install -r requirements.txt`

# How to use
1. Activate environment: `$ . venv/bin/activate.fish`
2. Run the script: `$ python eaglestitch.py -c etc/eaglestitch.conf`

# Available APIs
- Get all stithing results: `GET /stitching`
- Get a specific stithing result: `GET /stitching/{stitching_id}`