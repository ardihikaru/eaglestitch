import asab
from eagle_zenoh.extras.functions import is_img_exist
import logging

###

L = logging.getLogger(__name__)


###


class WebviewerService(asab.Service):

	def __init__(self, app, service_name="eaglestitch.WebviewerService"):
		super().__init__(app, service_name)

		self.stitching_api_svc = app.get_service("eaglestitch.StitchingAPIService")

		self.output_root_dir = asab.Config["stitching:config"]["root_output_dir"]
		self.img_not_found_path = asab.Config["webview"]["img_not_found_fname"]

	async def load_stitching_result(self, stitch_id):
		_, _, data = await self.stitching_api_svc.get_stitching_result(
			stitch_id=stitch_id,
			to_url=True,
			root_url=False,
		)

		if data is None:
			return {
				"img": self.img_not_found_path,
				"status": "<IMAGE NOT FOUND>",
			}

		# Data found, but there is no stitching result
		elif data is not None and not data["stitch_result"]["stitching_status"]:
			return {
				"img": self.img_not_found_path,
				"status": "<STITCHING FAILED>",
			}

		# Data found and stitching result is available, but the original file has been DELETED
		elif data is not None and not await self._is_image_exist(data):
			return {
				"img": self.img_not_found_path,
				"status": "<STITCHING SUCCEED, BUT FILE HAS BEEN DELETED>",
			}

		# Data found and stitching result is available
		else:
			return {
				"img": data["stitch_result"]["stitched_img_path"],
				"status": "<STITCHING SUCCEED>",
			}

	async def _is_image_exist(self, data):
		extracted_path = data["stitch_result"]["stitched_img_path"]
		img_true_path = "{}/{}".format(
			self.output_root_dir,
			extracted_path
		)
		return is_img_exist(img_true_path)
