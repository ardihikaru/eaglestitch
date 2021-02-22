import asab
import logging

###

L = logging.getLogger(__name__)


###


class ImageSubscriberService(asab.Service):

	def __init__(self, app, service_name="ImageSubscriberService"):
		super().__init__(app, service_name)

	async def initialize(self, app):
		# TODO: initialize Zenoh-net subscriber; open session
		await self.start_subscription()
		pass

	async def start_subscription(self):
		# TODO: implement subscription here
		import time
		while True:
			print(" --- @ start_subscription")
			time.sleep(1)
		pass
