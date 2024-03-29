## 0.7.1-stable (June 23, 2021)
  - Merge branch 'features/print-stitching-latency' into develop
  - log stitching latency
  - remove `\n`
  - remove `\n`
  - update readme
  - Merge branch 'release/v0.7.0-stable' into develop

## 0.7.0-stable (May 28, 2021)
  - Merge branch 'release/v0.7.0' into develop

## 0.7.0 (May 28, 2021)
  - Merge branch 'feature/update-readme' into develop
  - update how to run
  - Merge branch 'bugfix/add-cors-controller' into develop
  - add missing variable
  - Merge branch 'bugfix/add-cors-controller' into develop
  - add cors variable
  - update doc
  - add cors controller
  - Merge branch 'feature/bytes-size-calculator' into develop
  - add bytes size calculator
  - Merge pull request #3 from ardihikaru/bugfix/unable-to-read-extracted-images
  - add script to open result in webview
  - add options
  - add scripts to invoke APIs
  - add feature to enable/disable response with http path
  - bugfix: unable to read `to_url` variable
  - bugfix: change input filename
  - add input video and cvout config
  - update doc
  - remove opencv related lib; add `nanocamera` lib
  - bugfix: forgot to enable and assign `img_info` variable
  - add and implement `argparse`
  - backup old code
  - update comment
  - add `site.conf` template
  - Merge branch 'release/0.6' into develop

## 0.6.0 (March 24, 2021)
  - Merge branch 'feature/compress-img' into develop
  - add commented code for testing in university's environment
  - change printing into log warning
  - remove printing; disable force exit (used for debugging mode)
  - implement compressed tagged image consumer
  - remove printing; remove save to disk (used only for debugging)
  - add config to determine the zenoh consumer type
  - add test file for publishing tagged image (with my custom framework)
  - add `encrypt_str` function and add function descriptions
  - add common functions related with zenoh pubsub
  - enable/disable CV Out
  - add sample pubsub
  - add new feature to publish compressed images
  - - add new feature to compress image before sending via zenoh publisher - check extracted frame and convert it into fullHD (optional)
  - add sample to save to disk
  - bugfix: missmatch drone_id; change default `selector` and `peer`
  - comment image to disk function
  - code refactor: set `extra_len` as the total number of array elements
  - update test zenoh pubsub with compressed images
  - update test pubsub with int only
  - add notes
  - add examples pubsub image zenoh (compressed)
  - add examples pubsub image zenoh
  - add latency info
  - Merge branch 'release/0.5' into develop

## 0.5.0 (March 18, 2021)
  - Merge branch 'bugfix/stop-not-working-in-mode-2' into develop
  - code refactor
  - enrich information with `action_mode`
  - add processing latency for stitching pipeline
  - code refactor; bugfix: unable to read stop action properly
  - add different input files
  - add `ActionMode` class; code refactor
  - Merge branch 'release/0.4' into develop

## 0.4.0 (March 17, 2021)
  - Merge branch 'feature/live-config-update' into develop
  - bugfix: wrong stitching mode implementation; code refactor
  - implement publisher for live config update request
  - add new API: PUT /stitching/config
  - add new classes: `ConfigurableVars` and `StitchingMode`
  - Merge branch 'feature/stitch-mode' into develop
  - implement configurable stitching mode
  - add config to change stitching mode
  - add test code to publish all extracted frames
  - Merge branch 'release/0.3.1' into develop

## 0.3.1 (March 14, 2021)
  - Merge branch 'feature/readme-api' into develop
  - update fixed and more detail installation guide
  - remove `eclipse-zenoh` package
  - update available APIs; add available Web Pages
  - Merge branch 'release/0.3' into develop

## 0.3.0 (March 14, 2021)
  - Merge branch 'feature/webview-image' into develop
  - add config to enable/disable Stitching Processor on load system
  - add cropped stitching result into DB
  - - add static path source - add new endpoint to show stitched image result
  - add stitched image data loader
  - remove printing
  - add feature to enable/disable url-based response
  - add jinja template for showing stitching image result
  - add webview related config
  - add a function to check the existance of the image file
  - add image not found file
  - add `aiohttp-jinja2` lib
  - add base webview handler with index homepage
  - Merge branch 'feature/stitching-manager' into develop
  - remove todo: if stitching failed, it simply add status `False` when stored into DB
  - add new feature to START and STOP stitching via a Restful API
  - implement thread-based stitching execution
  - introduce config to execute stitching in a thread-level
  - Merge branch 'feature/stitch' into develop
  - bugfix: store input image paths
  - - code refactor - get stored input image paths
  - remove unused codes
  - - disable dummy print - load image input video file
  - - bugfix: fix wrong field name - add `input_imgs`
  - change image input type into a customized input
  - add config info
  - - code refactor - store source images by default (if enabled)
  - add more parameters related to stitching
  - add publisher based on video camera input
  - - code refactoring - complete the logic implementation
  - add config parameters related with stitching results
  - add core library
  - ignore `results` folder
  - refactor function into a class
  - ignore `site.conf`
  - remove unused dummy images
  - add dummy panorama input images
  - Added the code for removing black region
  - Added the code for stitching
  - add doc how to use zenoh publisher
  - add doc how to code on this class
  - fix typo
  - Merge branch 'release/0.2.1' into develop

## 0.2.1 (February 23, 2021)
  - Merge pull request #2 from ardihikaru/bugfix/code-refactor
  - - code refactor the logic on storing images into files - bugfix: wrong respone message in API - update comments
  - code refactor the logic on storing images into files
  - update comments
  - comment unused parameters and section
  - - update README file - delete unused file - rename test files
  - Merge branch 'release/0.2' into develop

## 0.2.0 (February 23, 2021)
  - Merge pull request #1 from ardihikaru/feature/based-framework
  - - update gitignore: ignore stored outputs - update the usage in README file - add image subscriber module - add stitching module - add stitching api module - update config file - add test scripts to pub/sub image-based data and normal data (dict/val) - update requirements file
  - add new module: `Stitching`
  - add new module: Image Subscriber
  - remove unused imports
  - add base RestFull framework (based on ASAB)
  - add requirement file
  - update gitignore
  - Merge branch 'feature/code-skeleton' into develop
  - added code skeleton

## 0.1.0 (July 20, 2020)
  - initial commit; added initial files
  - Initial commit

