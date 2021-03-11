

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
                # TODO: do stitching pipeline here

                # TODO: Expect to have `self.stitch_result` value updated
                """
                e.g.
                        self.stitch_result = {
                                "stitching_status": True,
                                "stitched_img_path": "./path/here/stit.jpg"
                        }
                """

                ### OpenCV Stitcher ###

                # Initialize OpenCV stitcher object
                if imutils.is_cv3():
                        cv_stitcher = cv2.createStitcher() 
                else:
                        cv_stitcher = cv2.Stitcher_create()
            
                # Perform image stitching
                (status, stitched_img) = cv_stitcher.stitch(stitcher.imgs)

                if status == 0:
                        self.stitch_result = {
                            "stitching_status": True,
                            "stitched_img_path": "/Users/tim/Desktop/devel/eaglestitch/sample-images/pano-5-eaglestitch.jpg"
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

import cv2, imutils

img1_path = "/Users/tim/Desktop/devel/eaglestitch/sample-images/pano-5/pano-5-1.jpeg"  # TODO: to update this
img1 = cv2.imread(img1_path)

img2_path = "/Users/tim/Desktop/devel/eaglestitch/sample-images/pano-5/pano-5-2.jpeg"  # TODO: to update this
img2 = cv2.imread(img2_path)

img3_path = "/Users/tim/Desktop/devel/eaglestitch/sample-images/pano-5/pano-5-3.jpeg" # TODO: to update this
img3 = cv2.imread(img3_path)

img4_path = "/Users/tim/Desktop/devel/eaglestitch/sample-images/pano-5/pano-5-4.jpeg"  # TODO: to update this
img4 = cv2.imread(img4_path)

_batch_num = 4
_imgs = [img1, img2, img3, img4]

stitcher = Stitch(
        imgs=_imgs,
        batch_num=_batch_num
)

stitcher.run()

_results = stitcher.get_stitch_result()
print("## RESULT = {}".format(_results))
