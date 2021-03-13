import asab
from .service import StitchingAPIService
from .stitching_result import StitchingResultSectionWebHandler
from .stitching_controller import StitchingControllerSectionWebHandler
import logging

###

L = logging.getLogger(__name__)


###


class StitchingAPIModule(asab.Module):

	def __init__(self, app):
		super().__init__(app)
		self.Service = StitchingAPIService(app)
		self.StitchingResultSectionWebHandler = StitchingResultSectionWebHandler(app)
		self.StitchingControllerSectionWebHandler = StitchingControllerSectionWebHandler(app)

	async def initialize(self, app):
		L.warning("[SYSTEM PREPARATION] Stitching API Module module is loaded.")
