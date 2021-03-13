import asab
from .service import WebviewerService
from .web_handler import WebviewHandler
import logging

###

L = logging.getLogger(__name__)


###


class WebviewerModule(asab.Module):

	def __init__(self, app):
		super().__init__(app)
		self.Service = WebviewerService(app)
		self.WebviewHandler = WebviewHandler(app)

	async def initialize(self, app):
		L.warning("[SYSTEM PREPARATION] Webviewer Module module is loaded.")
