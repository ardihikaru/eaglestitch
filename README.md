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

# Installation
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
8. Install and deploy mongo container: `$ docker run -d --name mongo-service --network host mongo`

# Installation (`Bash Shell` + `Real Environment`)
1. Install [Rust toolchain](https://rustup.rs/) (for Zenoh usage)
    - Install rustop: `$ curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh`
    - Load cargo: `$ source $HOME/.cargo/env`
    - Instal toolchain: `$ rustup toolchain install nightly`
2. Update **Host Machine**'s python3 pip version: `$ pip3 install --upgrade pip`
3. Install `Cython`: `$ pip3 install Cython`
4. Go to main project directory
5. Install requirements: `$ pip3 install -r requirements.txt`
6. Install openCV (optional): `$ pip3 install opencv-python`
    - **IMPORTANT**: It is highly recommended to install it manually for CUDA supported version.

# How to use
1. Download [data publisher](https://github.com/ardihikaru/eagle-data-publisher) project
    - Use tag `v0.0.1-pre-alpha1`
    - Place the project under the same ROOT directory with your `EagleStitch` project
        - e.g. `/home/s010132/devel/<HERE>`
2. Export related libs: 
    - Server Eaglestitch: `$ export PYTHONPATH=:/home/s010132/devel/eaglestitch/pycore/:/home/s010132/devel/eagle-data-publisher/pycore`
3. Run the script: `$ python eaglestitch.py -c etc/eaglestitch.conf`
4. Running zenoh publisher ([follow the tutorial](https://github.com/ardihikaru/eagle-data-publisher/blob/main/README.md)).
5. Live update config:
   ``` 
   curl --location --request PUT 'http://localhost:8888/stitching/config' \
    --header 'Content-Type: application/json' \
    --data-raw '{
        "processor_status": true,
        "stitching_mode": 2,
        
        "target_stitch": 6,
    
        "frame_skip": 1,
        "max_frames": 4
    }' 
   ```
    - **IMPORTANT**: Please ignore value of `stitching_mode` (keep it as `2`) and `target_stitch`
    - `frame_skip`: Set how many frames to skip. default=1.
        - When `frame_skip=1`, no frame will be skipped (30 FPS)
        - When `frame_skip=3`, it will skip every 3 frames. So it will collect frame `1, 4, 8, ..., dst` (10 FPS)
    - `max_frames`: Set total number of frames to be collected before applying the stitching method.
        - **FYI**: So far, we tested it up to `max_frames=10`
6. Get stitching results: `curl --location --request GET 'http://localhost:8888/stitching?to_url=true'`


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

References:
 - Stitching pipeline: https://github.com/tranleanh/image-panorama-stitching/blob/master/multi_image_pano.py
 - Black region cropping for panorama image: https://www.pyimagesearch.com/2018/12/17/image-stitching-with-opencv-and-python/
