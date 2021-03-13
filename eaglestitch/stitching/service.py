import asab
import asyncio
from .stitch import Stitch
import logging
from asab.log import LOG_NOTICE
from eaglestitch.image_subscriber.zenoh_pubsub.zenoh_net_publisher import ZenohNetPublisher
from concurrent.futures import ThreadPoolExecutor
import time

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

		# Thread executors
		self.executor = ThreadPoolExecutor(asab.Config["thread"].getint("num_executor"))
		self.threaded = asab.Config["stitching:config"].getboolean("threaded")

	def stitch(self, collected_imgs, batch_num):
		L.warning("[STICHING] PERFORMING STITCHING FOR THIS TUPLE OF IMAGES")

		# perform stitching
		if self.threaded:
			self._threaded_stitching_manager(collected_imgs, batch_num)
		else:
			self._exec_stitching(collected_imgs, batch_num)

		return True

	def _exec_stitching(self, collected_imgs, batch_num):
		stitch_status, stitch_result, input_imgs = self._stitch_imgs(collected_imgs, batch_num)
		if not stitch_status:
			return False
		L.warning("[STICHING] STITCHING SUCCEED!")

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

	def _threaded_stitching_manager(self, collected_imgs, batch_num):
		L.warning('[threaded_stitch_manager] Start a thread-based Stitching Manager')
		t0_thread = time.time()

		try:
			kwargs = {
				"collected_imgs": collected_imgs,
				"batch_num": batch_num
			}
			self.executor.submit(self._exec_stitching, **kwargs)
		except Exception as e:
			L.error("[threaded_stitch_manager] Somehow we unable to Start the Thread: {}".format(e))
		t1_thread = (time.time() - t0_thread) * 1000
		L.warning('[threaded_stitch_manager] Latency for Start Scheduler Manager (%.3f ms)' % t1_thread)

	def _stitch_imgs(self, imgs, batch_num):
		try:
			sticher = Stitch(imgs, batch_num, self.config)
			sticher.run()

			return True, sticher.get_stitch_result(), sticher.get_stored_input_imgs()
		except Exception as e:
			L.error("Stitching failed due to: `{}`".format(e))
			return False, None
