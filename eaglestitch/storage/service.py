import asab
import asyncio
import time
import simplejson as json
from bson.objectid import ObjectId
from concurrent.futures import ThreadPoolExecutor
from eaglestitch.image_subscriber.zenoh_pubsub.core.zenoh_net import ZenohNet
from eaglestitch.image_subscriber.zenoh_pubsub.zenoh_net_subscriber import ZenohNetSubscriber
import logging

###

L = logging.getLogger(__name__)


###


class StorageService(asab.Service):

	def __init__(self, app, service_name="eaglestitch.StorageService"):
		super().__init__(app, service_name)

		# load services
		self.db_storage = app.get_service("asab.StorageService")

		# Load Storage Message Consumer
		self.App.PubSub.subscribe("eaglestitch.StoragePubSub.message!", self._on_pubsub_storage)

	async def _on_pubsub_storage(self, event_type, data_message_json):
		"""
		This function acts as the action when any storage-message-related task is consumed (to be stored into DB)
		:param event_type: `event_type` value is `eaglestitch.StoragePubSub.message!`
		:param data_message_json: a dictionary consists of `code` and `message` keys
		:return:
		"""
		if await self.store_to_db(data_message_json["collection"], data_message_json["data"]) is None:
			L.error("[DATABASE] Storing document into `{}` collection Failed.".format(data_message_json["collection"]))
		else:
			L.warning("[DATABASE] Storing data to `{}` collection succeed.".format(data_message_json["collection"]))

	async def store_to_db(self, collection, doc):
		# Obtain upsertor object which is associated with given `collection` value
		# To create new object we keep default `version` to zero
		upsertor = self.db_storage.upsertor(collection)

		for _doc_key, _doc_data in doc.items():
			upsertor.set(_doc_key, _doc_data)

		obj_id = await upsertor.execute()

		# Debugging purpose; please disable this on production!
		# print("Stored ID:", obj_id)

		return obj_id

	async def get_from_db(self, collection, keys=None):
		resp_data = []
		coll = await self.db_storage.collection(collection)
		cursor = coll.find({})
		while await cursor.fetch_next:
			doc = cursor.next_object()
			if keys is not None:
				_doc = {}
				for key in keys:
					_doc[key] = doc[key]
				resp_data.append(_doc)
			else:
				resp_data.append(doc)

		return resp_data

	async def get_from_db_by_id(self, collection, obj_id, keys=None):
		try:
			doc = await self.db_storage.get(collection, ObjectId(obj_id))
			if keys is not None:
				_doc = {}
				for key in keys:
					_doc[key] = doc[key]
				return _doc
			return doc
		except KeyError as e:  # id not found
			return None
