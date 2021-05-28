import asab.web.rest
import aiohttp.web
from configurable_vars.configurable_vars import ConfigurableVars, StitchingMode
import logging
import aiohttp_cors
from extras.cors import CORS_OPTIONS

###

L = logging.getLogger(__name__)

###


class StitchingControllerSectionWebHandler(object):

	def __init__(self, app):
		self.App = app
		self.stitching_api_svc = app.get_service("eaglestitch.StitchingAPIService")

		# app.RESTWebContainer.WebApp.router.add_get('/stitching/trigger/{action}', self.capture_trigger_action)
		# app.RESTWebContainer.WebApp.router.add_put('/stitching/config', self.live_config_update)

		# setup routes
		resources = [
			app.RESTWebContainer.WebApp.router.add_get('/stitching/trigger/{action}', self.capture_trigger_action),
			app.RESTWebContainer.WebApp.router.add_put('/stitching/config', self.live_config_update)
		]

		# append cors to each route
		for res in resources:
			self.cors.add(res, CORS_OPTIONS)

		# initialize valid configurable vars
		self._valid_configurable_vars = frozenset([
			ConfigurableVars.PROCESSOR_STATUS.value,  # Boolean
			ConfigurableVars.STITCHING_MODE.value,  # Int
			ConfigurableVars.TARGET_STITCH.value,  # Int
			ConfigurableVars.FRAME_SKIP.value,  # Int
			ConfigurableVars.MAX_FRAMES.value,  # Int
		])

	async def capture_trigger_action(self, request):
		action = (request.match_info["action"]).lower()
		if action is None:
			L.error("`action` is missing from request.")
			raise aiohttp.web.HTTPBadRequest(reason="`action` is missing from request.")

		status, msg = await self.stitching_api_svc.control_stitching_behavior(
			action=action
		)

		# Here we received the barrier and we can respond 'OK'
		return asab.web.rest.json_response(request, {
			"status": "OK" if status == 200 else "NOK",
			"message": msg,
		}, status=status)

	async def _validate_request_json(self, request_json):
		for req_key in list(request_json.keys()):
			if req_key not in self._valid_configurable_vars:
				_err_msg = "Var `{}` is invalid.".format(req_key)
				L.error(_err_msg)
				return _err_msg

			# validate data type
			# `PROCESSOR_STATUS` is a Boolean
			if req_key == ConfigurableVars.PROCESSOR_STATUS.value and \
				not isinstance(request_json[req_key], bool):
				_err_msg = "Var `{}` should be a Boolean.".format(req_key)
				L.error(_err_msg)
				return _err_msg

			_valid_stitching_mode = frozenset([StitchingMode.BATCH.value, StitchingMode.STREAM.value])
			if req_key == ConfigurableVars.STITCHING_MODE.value and not isinstance(request_json[req_key], int):
				_err_msg = "Var `{}` should be an Integer.".format(req_key)
				L.error(_err_msg)
				return _err_msg
			if req_key == ConfigurableVars.STITCHING_MODE.value and request_json[req_key] not in _valid_stitching_mode:
				_err_msg = "Var `{}` valid value is `1` or `2`.".format(req_key)
				L.error(_err_msg)
				return _err_msg

			if req_key == ConfigurableVars.TARGET_STITCH.value and not isinstance(request_json[req_key], int):
				_err_msg = "Var `{}` should be an Integer.".format(req_key)
				L.error(_err_msg)
				return _err_msg
			if req_key == ConfigurableVars.TARGET_STITCH.value and isinstance(request_json[req_key], bool):
				_err_msg = "Var `{}` should be an Integer.".format(req_key)
				L.error(_err_msg)
				return _err_msg

			if req_key == ConfigurableVars.MAX_FRAMES.value and not isinstance(request_json[req_key], int):
				_err_msg = "Var `{}` should be an Integer.".format(req_key)
				L.error(_err_msg)
				return _err_msg
			if req_key == ConfigurableVars.MAX_FRAMES.value and isinstance(request_json[req_key], bool):
				_err_msg = "Var `{}` should be an Integer.".format(req_key)
				L.error(_err_msg)
				return _err_msg

			if req_key == ConfigurableVars.STITCHING_MODE.value and not isinstance(request_json[req_key], int):
				_err_msg = "Var `{}` should be an Integer.".format(req_key)
				L.error(_err_msg)
				return _err_msg
			if req_key == ConfigurableVars.STITCHING_MODE.value and isinstance(request_json[req_key], bool):
				_err_msg = "Var `{}` should be an Integer.".format(req_key)
				L.error(_err_msg)
				return _err_msg

		return None

	async def _build_configurable_vars(self, request_json):
		configurable_vars = {}
		for req_key in list(request_json.keys()):
			# if req_key in ConfigurableVars().valid_vars():
			if req_key in self._valid_configurable_vars:
				configurable_vars[req_key] = request_json[req_key]

		return configurable_vars

	async def live_config_update(self, request):
		try:
			request_json = await request.json()
		except Exception as e:
			L.error("Unable to extract json request")
			raise aiohttp.web.HTTPBadRequest(reason="Unable to extract json request")

		# Validate request json
		_err_msg = await self._validate_request_json(request_json)
		if _err_msg is not None:
			raise aiohttp.web.HTTPBadRequest(reason=_err_msg)

		# build configurable var objects
		configurable_vars = await self._build_configurable_vars(request_json)

		status, msg, data = await self.stitching_api_svc.update_config(
			configurable_vars=configurable_vars
		)

		# Here we received the barrier and we can respond 'OK'
		return asab.web.rest.json_response(request, {
			"status": "OK" if status == 200 else "NOK",
			"message": msg,
			"data": data,
		}, status=status)
