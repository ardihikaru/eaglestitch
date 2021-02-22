import asab.web.rest
import aiohttp.web
import logging

###

L = logging.getLogger(__name__)

###


class StitchingResultSectionWebHandler(object):

	def __init__(self, app):
		self.App = app
		self.stitching_api_svc = app.get_service("StitchingAPIService")

		app.RESTWebContainer.WebApp.router.add_get('/stitching', self.get_stitching)
		app.RESTWebContainer.WebApp.router.add_get('/stitching/{stitched_id}', self.get_stitching_by_id)

	async def get_stitching(self, request):
		status, msg, data = await self.stitching_api_svc.get_stitching_result()

		# Here we received the barrier and we can respond 'OK'
		return asab.web.rest.json_response(request, {
			"status": "OK" if status == 200 else "NOK",
			"message": msg,
			"data": data,
		}, status=status)

	async def get_stitching_by_id(self, request):
		stitched_id = (request.match_info["stitched_id"]).upper()
		if stitched_id is None:
			L.error("`stitched_id` is missing from request.")
			raise aiohttp.web.HTTPBadRequest()

		status, msg, data = await self.stitching_api_svc.get_stitching_result(
			stitched_id=stitched_id
		)

		# Here we received the barrier and we can respond 'OK'
		return asab.web.rest.json_response(request, {
			"status": "OK" if status == 200 else "NOK",
			"message": msg,
			"data": data,
		}, status=status)
