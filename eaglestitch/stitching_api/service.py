import asab
import logging

###

L = logging.getLogger(__name__)


###


class StitchingAPIService(asab.Service):

	COLLECTION_NAME = "stitchedImages"

	FN_ID = "_id"
	FN_V = "_v"
	FN_C = "_c"
	FN_M = "_m"

	FN_STITCH_IMG_RESULT = "stitch_result"
	FN_INPUT_IMGS = "input_imgs"

	class ErrorMessage(object):
		REQUEST_TIMEOUT = "REQUEST TIMEOUT"
		BAD_REQUEST = "BAD REQUEST"
		INVALID_TRIGGER_ACTION = "INVALID TRIGGER ACTION"

	class TriggerType(object):
		START = "start"
		STOP = "stop"

	def __init__(self, app, service_name="eaglestitch.StitchingAPIService"):
		super().__init__(app, service_name)

		# load services
		self.storage_svc = app.get_service('eaglestitch.StorageService')

		# list valid keys in this collection (to be shown)
		self.keys = frozenset([
			self.FN_ID,
			self.FN_INPUT_IMGS,
			self.FN_STITCH_IMG_RESULT,
		])

		# set available trigger types
		self._valid_actions = frozenset([
			self.TriggerType.START,
			self.TriggerType.STOP
		])

	async def get_stitching_result(self, stitched_id=None):
		# initialize default response
		_status, _msg, _data = 200, None, None

		if stitched_id is not None:  # find by id
			_data = await self.storage_svc.get_from_db_by_id(self.COLLECTION_NAME, stitched_id, self.keys)
			if _data is None:
				L.error("Data not found.")
				_msg = "Data not found."
			else:
				_msg = "Data found."
		else:
			_data = await self.storage_svc.get_from_db(self.COLLECTION_NAME, self.keys)

		return _status, _msg, _data

	async def control_stitching_behavior(self, action):
		# initialize default response
		_status, _msg = 200, None

		# Validate action
		if action not in self._valid_actions:
			return 400, self.ErrorMessage.INVALID_TRIGGER_ACTION

		# get processor's action to do
		_enable_processor = True if action == self.TriggerType.START else False

		# control stitching action based on the user request
		# by publishing an action and will be captured by Stitching Manager Subscriber
		self.App.PubSub.publish(
			"eaglestitch.StitchingManagerPubSub.message!",
			enable_processor=_enable_processor,
			asynchronously=True,
		)

		# generate message to response the request
		_msg = "EagleStitch System has been notified with `{}` action!".format(action.upper())

		return _status, _msg
