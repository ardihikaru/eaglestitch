class Stitch(object):
        """
        This class perform image stitching by taking two parameters:
        - imgs: list of images (numpy array)
        - batch_num: total number of images to be stitched
        """
        def __init__(self, imgs, batch_num):
                self.batch_num = batch_num
                self.imgs = imgs
                self.stitch_result = None

        def run(self):
                print("I am running stitching now")

                ### OpenCV Stitcher ###

                # Initialize OpenCV stitcher object
                if imutils.is_cv3():
                        cv_stitcher = cv2.createStitcher() 
                else:
                        cv_stitcher = cv2.Stitcher_create()
            
                # Perform image stitching
                (status, stitched_img) = cv_stitcher.stitch(stitcher.imgs)

                ### End  ###

                if status == 0:
                        self.stitch_result = {
                            "stitching_status": True,
                            "stitched_img_path": "/Users/tim/Desktop/devel/eaglestitch/sample-images/pano-5-eaglestitch-output.jpg"
                        }

                        # Store stitched_img to disk
                        cv2.imwrite(self.stitch_result["stitched_img_path"], stitched_img)
                else:
                        self.stitch_result = {
                            "stitching_status": False 
                        }

                pass

        def get_stitch_result(self):
                print("I am collecting the result")
                return self.stitch_result

#####

import cv2, imutils
from imutils import paths

print('I am loading images ...')

source_path = '/Users/tim/Desktop/devel/eaglestitch/sample-images/pano-5/'
img_source = sorted(list(paths.list_images(source_path)))

_batch_num = 0
_imgs = []

for an_img in img_source:
    img_temp = cv2.imread(an_img)
    _imgs.append(img_temp)
    _batch_num = _batch_num + 1
    
stitcher = Stitch(
        imgs=_imgs,
        batch_num=_batch_num
)

stitcher.run()

_results = stitcher.get_stitch_result()
print("## RESULT = {}".format(_results))
