# eaglestitch
Eagle Stitch is a dockerized system aims to stitch multiple images

# Technology stack
1. Python version >=3.6 ([related issue](https://github.com/eclipse-zenoh/zenoh-python/commit/0e9b37780730b13b827e949e941922f53e5626b4))
2. Python [ASAB Framework](https://github.com/TeskaLabs/asab) as the base code
3. [Zenoh PubSub](http://zenoh.io/)
4. [Mongo Database](https://www.mongodb.com/)
5. Zenoh API wrapper: [Zenoh-as-a-Service](https://github.com/ardihikaru/zenoh-as-a-service)
6. [Rust](https://www.rust-lang.org/) as the base code of [Zenoh](http://zenoh.io/)

# Installation
1. Install [Rust toolchain](https://rustup.rs/) (for Zenoh usage)
    - Install rustop: `$ sudo snap install rustup --classic`
    - Instal toolchain: `$ rustup toolchain install nightly`
1. Go to main project directory
2. Install python virtual environment: `$ python3 -m venv venv`
3. Execute these comamnds before installing **Zenoh**:
    ```
    $ pip install --upgrade pip
    $ pip install maturin
    ```
4 Install requirements: `$ pip install -r requirements.txt`

# How to use
1. Activate environment: `$ . venv/bin/activate.fish`
2. Run the script: `$ python eaglestitch.py -c etc/eaglestitch.conf`
3. Running Zenoh publisher: `$ python tests/net_publisher_img.py`

# Common information
- RestAPI URL: `$ http://<domain>:8888`

# Available APIs
- Get all stithing results: `GET /stitching`
- Get a specific stithing result: `GET /stitching/{stitching_id}`