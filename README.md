# eaglestitch
Eagle Stitch is a dockerized system aims to stitch multiple images

# Technology stack
1. Python version >=3.6 ([related issue](https://github.com/eclipse-zenoh/zenoh-python/commit/0e9b37780730b13b827e949e941922f53e5626b4))
2. Python [ASAB Framework](https://github.com/TeskaLabs/asab) as the base code
3. [Zenoh PubSub](http://zenoh.io/)
4. [Mongo Database](https://www.mongodb.com/)
5. Zenoh API wrapper: [Zenoh-as-a-Service](https://github.com/ardihikaru/zenoh-as-a-service)
6. [Rust](https://www.rust-lang.org/) as the base code of [Zenoh](http://zenoh.io/)
7. [Fish Shell](https://github.com/fish-shell/fish-shell) 
    and [Oh-My-Fish](https://github.com/oh-my-fish/oh-my-fish) (**OPTIONAL, but recommended**)

# Installation (`Fish Shell` + `Virtual ENV`)
1. Install [Rust toolchain](https://rustup.rs/) (for Zenoh usage)
    - Install rustop: `$ curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh`
    - Install `Rustup` plugin:
        `$ omf install rustup`
    - Instal toolchain: `$ rustup toolchain install nightly`
2. Update and install `pip3`
    - `$ sudo apt update`
    - `$ sudo apt install python3-pip`
3. Update **Host Machine**'s python3 pip version: `$ pip3 install --upgrade pip`
4. Install following package in **Host Maching**:
    - Eclipse-Zenoh: `$ pip3 install eclipse-zenoh`
5. Go to main project directory
6. Install requirements: `$ pip install -r requirements.txt`
7. Install openCV: `$ pip install opencv-python`

# Installation (`Bash Shell` + `Real Environment`)
1. Install [Rust toolchain](https://rustup.rs/) (for Zenoh usage)
    - Install rustop: `$ curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh`
    - Load cargo: `$ source $HOME/.cargo/env`
    - Instal toolchain: `$ rustup toolchain install nightly`
2. Update **Host Machine**'s python3 pip version: `$ pip3 install --upgrade pip`
3. Install following package in **Host Maching**:
    - Maturin: `$ pip3 install maturin`
    - Eclipse-Zenoh: `$ pip3 install eclipse-zenoh`
4. Go to main project directory
5. Install python virtual environment: `$ python3 -m venv venv`
6. Activate python virtual environment: `$ . venv/bin/activate.fish`
7. Install requirements: `$ pip install -r requirements.txt`
    - **IMPORTANT NOTE**: Package `eclipse-zenoh` is already installed in `step-3`
8. Install openCV: `$ pip install opencv-python`
9. Install Zenoh API connector (with Rust-based Zenoh):
    - Go to `venv` directory: `$ cd venv`
    - Clone zenoh: `$ git clone https://github.com/eclipse-zenoh/zenoh-python.git`
    - Go to cloned Zenoh directory: `$ cd zenoh-python`
    - Build the package: `$ maturin develop —release`
        - **IF ERROR happened**, use this command instead:
            $ pip install . --use-feature=in-tree-build`


# How to use
1. Go to root project directory: `$ cd /../eaglestitch/`
2. Activate python virtual environment: `$ . venv/bin/activate.fish`
3. Run the script: `$ python eaglestitch.py -c etc/eaglestitch.conf`
4. Running Zenoh publisher: `$ python tests/net_publisher_img_camera.py -e tcp/localhost:7446 --cvout -v /home/ardi/devel/nctu/IBM-Lab/eaglestitch/data/videos/samer/0312_1_LtoR_1.mp4`
    - You can change `localhost` to a specific IP, and
    - You can change `/home/ardi/devel/nctu/IBM-Lab/eaglestitch/data/videos/samer/0312_1_LtoR_1.mp4` into:
        - Another video file (with **full path**), or
        - Change it into `0` to read camera

# Common information
- RestAPI URL: `$ http://<domain>:8888`

# Available APIs
- Get all stithing results: `GET /stitching`
- Get a specific stithing result: `GET /stitching/{stitching_id}`
- Ask system to **START** the **stitching processor**: `GET /stitching/trigger/start`
- Ask system to **STOP** the **stitching processor**: `GET /stitching/trigger/stop`

# Available WebViews
- Homepage: `http://localhost:8888`
- Show stitching result: `http://localhost:8888/webview/{stitching_id}`

Reference:
 - Stitching pipeline: https://github.com/tranleanh/image-panorama-stitching/blob/master/multi_image_pano.py
 - Black region cropping for panorama image: https://www.pyimagesearch.com/2018/12/17/image-stitching-with-opencv-and-python/

