import asab.web.rest
import aiohttp.web
import logging

###

L = logging.getLogger(__name__)

###


class StitchingControllerSectionWebHandler(object):

	def __init__(self, app):
		self.App = app
		self.stitching_api_svc = app.get_service("eaglestitch.StitchingAPIService")

		app.RESTWebContainer.WebApp.router.add_get('/stitching/trigger/{action}', self.capture_trigger_action)

	async def capture_trigger_action(self, request):
		print("## capture_trigger_action")
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
