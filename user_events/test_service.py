""" Example of service unit testing best practice. """

from nameko.testing.services import worker_factory
from user_events import UserEventsService
import json

def test_send():
    # create worker with mock dependencies
    service = worker_factory(UserEventsService)

    new_user_event = {
            'id': 'id',
            'address': {
                'city': 'London',
                'state': '',
                'country': 'UK',
                'postCode': 'WE1'
            },
            'datetime': '2020-11-10 12:12:30.444'
        }

    # test send service rpc method
    result = service.send(new_user_event)

    # Validate that we call kafka producer flush once
    service.producer.flush.assert_called_once()
