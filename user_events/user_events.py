import json
import logging

from nameko.dependency_providers import Config
from nameko.rpc import rpc
from nameko_kafka import KafkaProducer


class UserEventsService:
    """   User events  """
    name = "userevents"
    config = Config()
    producer = KafkaProducer()
    
    def _on_send_error(self, excp):
        logging.error('Error sending message', exc_info=excp)
        # handle exception
        # Note: implement a retry logic, or a dead letter queue, ...


    def serialise_message(self, message: dict) -> bytes:
        return json.dumps(message).encode('utf-8')


    def send_message(self, message: dict):
        future = self.producer.send("user_event", value=self.serialise_message(message))
        future.add_errback(self._on_send_error)


    @rpc
    def send(self, user_event):
        self.send_message(message=user_event)
        self.producer.flush()
        logging.info(f'New user event {user_event}')
