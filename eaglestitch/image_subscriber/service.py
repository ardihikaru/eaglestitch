import asab
import logging

###

L = logging.getLogger(__name__)


###


class ImageSubscriberService(asab.Service):

	def __init__(self, app, service_name="ImageSubscriberService"):
		super().__init__(app, service_name)

		self.stitching_svc = app.get_service("StitchingService")
		self.batch_num = 0  # we will reset this value once finished sending tuple of imgs into stitching service
		self.batch_imgs = []  # we will reset this value once finished sending tuple of imgs into stitching service
		self.target_stitch = asab.Config["stitching:config"].getint("target_stitch")

	async def initialize(self, app):
		# TODO: initialize Zenoh-net subscriber; open session
		await self.start_subscription()
		pass

	async def start_subscription(self):
		# TODO: implement subscription here
		import time
		while True:  # this is simply to illustrate how the system capture each img and perform the stitching pipeline
			self.batch_num += 1
			print(" ### batch_num-{}".format(self.batch_num))
			time.sleep(1)

			# TODO: append current captured img data
			img_data = []  # this is dummy img data
			self.batch_imgs.append(img_data)

			# this is sample code on how to perform stitching
			# TODO: when N number of images has been collected, send the tuple of images into stitching service
			if self.batch_num == self.target_stitch:
				# Send this tuple of imgs into stitching
				await self.stitching_svc.stitch(self.batch_imgs)

				# Reset the value
				self.batch_num = 0
				self.batch_imgs = []

		pass
