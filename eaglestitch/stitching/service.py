import asab
import asyncio
from .stitch import Stitch
import logging
from asab.log import LOG_NOTICE
from eaglestitch.image_subscriber.zenoh_pubsub.zenoh_net_publisher import ZenohNetPublisher

###

L = logging.getLogger(__name__)


###


class StitchingService(asab.Service):

	def __init__(self, app, service_name="eaglestitch.StitchingService"):
		super().__init__(app, service_name)

		self.storage_svc = app.get_service("eaglestitch.StorageService")
		self.stitching_col = asab.Config["stitching:config"]["collection"]

		# setup config variables
		self.config = {
			"root_output_dir": asab.Config["stitching:config"]["root_output_dir"],
			"store_input_imgs": asab.Config["stitching:config"].getboolean("store_input_imgs"),
			"crop": asab.Config["stitching:config"].getboolean("crop"),
			"source_img_name": asab.Config["stitching:config"]["source_img_name"],
			"stitched_img_name": asab.Config["stitching:config"]["stitched_img_name"],
			"crop_stitched_img_name": asab.Config["stitching:config"]["crop_stitched_img_name"],
		}

	def stitch(self, collected_imgs, batch_num):
		L.warning("[STICHING] PERFORMING STITCHING FOR THIS TUPLE OF IMAGES")

		# perform stitching
		stitch_status, stitch_result = self._stitch_imgs(collected_imgs, batch_num)
		if not stitch_status:
			return False
		L.warning("[STICHING] STITCHING SUCCEED!")
		# L.log(LOG_NOTICE, "[STICHING] STITCHING SUCCEED!")

		# if stitching succeed: [1] store stitched images into output directory
		if stitch_status:
			self._save_stitched_imgs_to_disk(stitch_result)
		L.warning("[STICHING] STITCHING RESULT HAS BEEN STORED!")
		# L.log(LOG_NOTICE, "[STICHING] STITCHING RESULT HAS BEEN STORED!")

		# if stitching succeed: [2] store input images into output directory
		input_imgs = self._save_input_imgs_to_disk(collected_imgs)
		L.warning("[STICHING] INPUT IMAGES HAS BEEN STORED!")
		# L.log(LOG_NOTICE, "[STICHING] INPUT IMAGES HAS BEEN STORED!")

		# if storing images succeed, save all those information into database
		data_message_json = {
			"collection": self.stitching_col,
			"data": {
				"stitch_result": stitch_result,
				"input_imgs": input_imgs,
			}
		}
		self.App.PubSub.publish(
			"eaglestitch.StoragePubSub.message!",
			data_message_json=data_message_json,
			asynchronously=True,
		)

		L.warning("[STICHING] STITCHING RESULT INFORMATION HAS BEEN LOGGED INTO DATABASE!")
		# L.log(LOG_NOTICE, "[STICHING] STITCHING RESULT INFORMATION HAS BEEN LOGGED INTO DATABASE!")

		return True

	def _stitch_imgs(self, imgs, batch_num):
		try:
			sticher = Stitch(imgs, batch_num, self.config)
			sticher.run()

			return True, sticher.get_stitch_result()
		except Exception as e:
			L.error("Stitching failed due to: `{}`".format(e))
			return False, None

	def _save_stitched_imgs_to_disk(self, stitch_result):
		self.storage_svc.save_img_to_disk(stitch_result)

	def _save_input_imgs_to_disk(self, collected_imgs):
		stored_imgs = []
		for img in collected_imgs:
			stored_img = self.storage_svc.save_img_to_disk(img)
			if stored_img is not None:
				stored_imgs.append(stored_img)

		return stored_imgs
