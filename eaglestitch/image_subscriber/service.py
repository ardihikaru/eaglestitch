import asab
import asyncio
import time
import numpy as np
from datetime import datetime
from eaglestitch.image_subscriber.zenoh_pubsub.core.zenoh_net import ZenohNet
from eaglestitch.image_subscriber.zenoh_pubsub.zenoh_net_subscriber import ZenohNetSubscriber
import logging
from concurrent.futures import ThreadPoolExecutor

###

L = logging.getLogger(__name__)


###


class ImageSubscriberService(asab.Service):

	class ErrorCode(object):
		ERR_ZENOH_MODE = "system_err_001"
		ERR_ZENOH_SUBSCRIPTION = "system_err_002"
		ERR_REDIS_MODE = "system_err_003"
		ERR_SUBSCRIPTION_SELECTOR = "system_err_004"

	class PubSubMode(object):
		ZENOH = "zenoh"
		REDIS = "redis"

	def __init__(self, app, service_name="eaglestitch.ImageSubscriberService"):
		super().__init__(app, service_name)

		# load services
		self.System_manager = app.get_service('eaglestitch.SystemManagerService')
		self.stitching_svc = app.get_service("eaglestitch.StitchingService")

		self.batch_num = 0  # we will reset this value once finished sending tuple of imgs into stitching service
		self.batch_imgs = []  # we will reset this value once finished sending tuple of imgs into stitching service
		self.target_stitch = asab.Config["stitching:config"].getint("target_stitch")
		# input and target stitched image resolution
		self.img_w = asab.Config["stitching:config"].getint("img_w")
		self.img_h = asab.Config["stitching:config"].getint("img_h")
		self.img_ch = asab.Config["stitching:config"].getint("img_ch")

		self.pubsub_mode = asab.Config["pubsub:config"]["mode"]

		# config zenoh pubsub config
		self.zenoh_comm_protocol = asab.Config["zenoh:config"]["comm_protocol"]
		self.zenoh_comm_ip = asab.Config["zenoh:config"]["comm_ip"]
		self.zenoh_comm_port = asab.Config["zenoh:config"]["comm_port"]
		self.selector = asab.Config["zenoh:config"]["selector"]
		self.listener = "{}/{}:{}".format(
			self.zenoh_comm_protocol,
			self.zenoh_comm_ip,
			self.zenoh_comm_port,
		)
		self.sub_svc = None
		self.subscriber = None

	async def initialize(self, app):
		# validate PubSub mode
		if await self._validate_pubsub_mode():
			await self.subscription()

	async def _validate_pubsub_mode(self):
		_valid_mode = frozenset([
			self.PubSubMode.ZENOH,
			self.PubSubMode.REDIS
		])
		if self.pubsub_mode not in _valid_mode:
			_err_msg = ">>>>> Invalid PubSub mode; Available mode: `zenoh` and `redis`"
			L.error(_err_msg)
			await self.System_manager.publish_error(
				system_code=self.ErrorCode.ERR_ZENOH_MODE,
				system_message=_err_msg
			)

			return False

		return True

	def img_listener(self, consumed_data):
		self.batch_num += 1

		# For debugging only; please comment it once done the debugging session
		# print(" ######### self.batch_num = ", self.batch_num)

		t0_decoding = time.time()
		deserialized_bytes = np.frombuffer(consumed_data.payload, dtype=np.int8)
		t1_decoding = (time.time() - t0_decoding) * 1000
		L.warning(
			('[%s] Latency load ONLY numpy image (%.3f ms)' % (datetime.now().strftime("%H:%M:%S"), t1_decoding)))

		t0_decoding = time.time()
		deserialized_img = np.reshape(deserialized_bytes, newshape=(self.img_w, self.img_h, self.img_ch))
		# print(">>> img_ori SHAPE:", deserialized_img.shape)
		t1_decoding = (time.time() - t0_decoding) * 1000
		L.warning(
			('[%s] Latency reformat image (%.3f ms)' % (datetime.now().strftime("%H:%M:%S"), t1_decoding)))

		# TODO: append current captured img data
		self.batch_imgs.append(deserialized_img)

		# this is sample code on how to perform stitching
		# TODO: when N number of images has been collected, send the tuple of images into stitching service
		if self.batch_num == self.target_stitch:
			# Send this tuple of imgs into stitching
			try:
				if not self.stitching_svc.stitch(self.batch_imgs, self.batch_num):
					L.error("Stitching failed")
					# TODO: If stitching failed, what's the behavior?
			except Exception as e:
				L.error("Stitching pipiline failed. Reason: {}".format(e))

			# Reset the value
			self.batch_num = 0
			self.batch_imgs = []

	def _start_zenoh(self):
		self.sub_svc = ZenohNetSubscriber(
			_selector=self.selector, _session_type="SUBSCRIBER", _listener=self.listener
		)
		self.sub_svc.init_connection()

		self.sub_svc.register(self.img_listener)
		self.subscriber = self.sub_svc.get_subscriber()

	# once module stopped, stop the subscription
	async def finalize(self, app):
		await self._stop_subscription()

	async def _start_zenoh_subscription(self):
		try:
			executor = ThreadPoolExecutor(1)
			executor.submit(self._start_zenoh)
		except Exception as e:
			_err_msg = ">>>>> ZENOH Subscription Failed; Reason: `{}`".format(e)
			L.error(_err_msg)
			await self.System_manager.publish_error(
				system_code=self.ErrorCode.ERR_ZENOH_SUBSCRIPTION,
				system_message=_err_msg
			)

	# TODO: implement Redis Subscription
	async def _start_redis_subscription(self):
		_err_msg = ">>>>> REDIS Subscription function is not implemeted yet."
		L.error(_err_msg)
		await self.System_manager.publish_error(
			system_code=self.ErrorCode.ERR_REDIS_MODE,
			system_message=_err_msg
		)

	async def _stop_subscription(self):
		if self.pubsub_mode == self.PubSubMode.ZENOH:
			self.sub_svc.close_connection(self.subscriber)

	async def subscription(self):
		if self.pubsub_mode == self.PubSubMode.ZENOH:
			await self._start_zenoh_subscription()
		elif self.pubsub_mode == self.PubSubMode.REDIS:
			# TODO: implement mode Redis PubSub
			await self._start_redis_subscription()
		else:
			_err_msg = ">>>>> Subscription failed."
			L.error(_err_msg)
			await self.System_manager.publish_error(
				system_code=self.ErrorCode.ERR_SUBSCRIPTION_SELECTOR,
				system_message=_err_msg
			)
