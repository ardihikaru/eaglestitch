import aiohttp
import asyncio
import asab
import logging

###

L = logging.getLogger(__name__)


###


class StitchingAPIService(asab.Service):

	class ErrorMessage(object):
		REQUEST_TIMEOUT = "REQUEST TIMEOUT"
		BAD_REQUEST = "BAD REQUEST"

	def __init__(self, app, service_name="StitchingAPIService"):
		super().__init__(app, service_name)

	async def _validate_stitched_id(self, stitched_id):
		# TODO: check document in database, exist of not
		return True  # TODO: change the value accordingly

	async def get_stitching_result(self, stitched_id=None):
		# initialize default response
		_status, _status_code, _msg, _data = None, None, None, None

		if stitched_id is not None and not await self._validate_stitched_id(stitched_id):
			L.error("Data not found.")
			_msg = "Data not found."

		_status, _msg, _data = 200, "Request OK", None
		return _status, _msg, _data
