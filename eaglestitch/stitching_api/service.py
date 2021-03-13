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

		# static path name
		self.static_path_name = asab.Config["eaglestitch:rest"]["static_path_name"]

		# get base URL for all stored images (stitching results and source images)
		self.img_url = "{}://{}/{}".format(
			asab.Config["eaglestitch:rest"]["schema"],
			asab.Config["eaglestitch:rest"]["listen"],
			self.static_path_name,
		)

	async def get_stitching_result(self, stitch_id=None, to_url=False, root_url=True):
		# initialize default response
		_status, _msg, _data = 200, None, None

		try:
			if stitch_id is not None:  # find by id
				_data = await self.storage_svc.get_from_db_by_id(self.COLLECTION_NAME, stitch_id, self.keys)
				if _data is None:
					L.error("Data not found.")
					_msg = "Data not found."
				else:
					_msg = "Data found."

					if to_url:
						_data = await self._convert_all_paths_to_url(_data, root_url)
			else:
				_data = await self.storage_svc.get_from_db(self.COLLECTION_NAME, self.keys)
		except Exception as e:  # id not found
			return 400, str(e), None

		return _status, _msg, _data

	async def _convert_all_paths_to_url(self, result, root_url):
		# convert stitching result from file path into URL
		if result["stitch_result"].get("stitching_status"):
			result["stitch_result"]["stitched_img_path"] = await self._stitch_img_path_to_url(
				result["stitch_result"].get("stitched_img_path"),
				root_url
			)

		# convert all source images from file paths into URLs (if any)
		if len(result.get("input_imgs")) > 0:
			_input_imgs = []
			for img in result.get("input_imgs"):
				_input_imgs.append(
					await self._input_img_path_to_url(img, root_url)
				)
			result["input_imgs"] = _input_imgs

		return result

	async def _input_img_path_to_url(self, fpath, root_url):
		extracted_path = fpath.split("/")

		if root_url:
			return "{}/{}/{}/{}".format(
				self.img_url,
				extracted_path[-3],
				extracted_path[-2],
				extracted_path[-1],
			)
		else:
			return "{}/{}/{}".format(
				extracted_path[-3],
				extracted_path[-2],
				extracted_path[-1],
			)

	async def _stitch_img_path_to_url(self, fpath, root_url):
		extracted_path = fpath.split("/")

		if root_url:
			return "{}/{}/{}".format(
				self.img_url,
				extracted_path[-2],
				extracted_path[-1],
			)
		else:
			return "{}/{}".format(
				extracted_path[-2],
				extracted_path[-1],
			)

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
