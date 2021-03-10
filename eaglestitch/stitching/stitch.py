

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
		pass

	def get_stitch_result(self):
		print("I am collecting the result")
		return self.stitch_result

"""

import cv2

img1_path = "/home/s010132/devel/eagleeye/data/out1.png"  # TODO: to update this
img1 = cv2.imread(img1_path)

img2_path = "/home/s010132/devel/eagleeye/data/out1.png"  # TODO: to update this
img2 = cv2.imread(img2_path)

_batch_num = 2
_imgs = [img1, img2]

stitcher = Stitch(
	imgs=_imgs,
	batch_num=_batch_num
)

stitcher.run()

_results = stitcher.get_stitch_result()
print("## RESULT = {}".format(_results))

"""