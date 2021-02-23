

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
		return self.stitch_result
