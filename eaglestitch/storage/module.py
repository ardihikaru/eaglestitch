import asab
from .service import StorageService
import logging

###

L = logging.getLogger(__name__)


###


class StorageModule(asab.Module):

	def __init__(self, app):
		super().__init__(app)
		self.Service = StorageService(app)

	async def initialize(self, app):
		L.warning("[SYSTEM PREPARATION] Storage Module module is loaded.")
