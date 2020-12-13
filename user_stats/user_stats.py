import datetime
import json
import logging

import yagmail
from nameko.dependency_providers import Config
from nameko.rpc import rpc
from nameko.timer import timer
from nameko_kafka import consume
from nameko_sqlalchemy import Database
from sqlalchemy import Column, String, create_engine, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base

DeclarativeBase = declarative_base()

class User(DeclarativeBase):
    __tablename__ = "users"
    id = Column(String, primary_key=True)
    user_id = Column(String)
    city = Column(String)
    state = Column(String)
    country = Column(String)
    post_code = Column(String)
    datetime = Column(String)

    def __init__(self,
                 seq_id,
                 user_id,
                 city,
                 state,
                 country,
                 post_code,
                 datetime):
        self.id = seq_id
        self.user_id = user_id
        self.city = city
        self.state = state
        self.country = country
        self.post_code = post_code
        self.datetime = datetime

engine = create_engine('sqlite:///data.db', echo = True)
DeclarativeBase.metadata.create_all(engine)
SEND_EMAIL = False
REPORT_PERIOD = 5 if not SEND_EMAIL else 3600
EMAIL_SOURCE = 'myemail@mailserver.com'
EMAIL_PASSWORD = 'mypassword'

class UserStats:
    """    User stats  service  """

    name = "userstats"
    config = Config()
    db = Database(DeclarativeBase)

    
    @consume("user_event", group_id="user_event")
    def consume_user_event(self, new_user_event: bytes):
        """ Subcribe user_event topic and update database """
        user = self._deserialise_message(message=new_user_event.value)
        record_id = f'{new_user_event.topic}-{new_user_event.offset}-{new_user_event.timestamp}'
        self._insert_new_user(record_id, user) 

    @rpc
    def report(self):
        """ Return user count by city """
        return self._get_report()

    @timer(interval=REPORT_PERIOD)
    def email_report(self):
        """ Email will be sent only if SEND_EMAIL false """
        report = self._get_report()
        to = ['manage@mybusiness.com']
        subject = 'report'
        content = str(report)

        if not SEND_EMAIL:
            logging.info(f"New report generated. Fake email sent. to: {to}, subject: {subject}, content: {content}")
            return

        yag = yagmail.SMTP(EMAIL_SOURCE, EMAIL_PASSWORD)
        yag.send(cc=to.encode('utf-8'),
                 subject=subject.encode('utf-8'),
                 contents=content.encode('utf-8'))
        logging.info(f"Email sent. to: {to}, subject: {subject}, content: {content}")

    def _deserialise_message(self, message: bytes) -> dict:
        return json.loads(message.decode('utf-8'))

    def _insert_new_user(self, record_id: str, user: dict):
        user_db_record = User(
            seq_id=record_id,
            user_id=user['id'],
            city=user.get('address', {}).get('city',''),
            state=user.get('address', {}).get('state',''),
            country=user.get('address', {}).get('country',''),
            post_code=user.get('address', {}).get('postCode',''),
            datetime=user.get('datetime', ''))

        with self.db.get_session() as session:
            try:
                session.add(user_db_record)
                session.commit()
            except IntegrityError:
                logging.info('Duplicated event')

        logging.info(f'New user inserted: {user}')

    def _get_user_count_by_city(self):
        with self.db.get_session() as session:
            result = (session \
                .query(
                    User.city,
                    func.count(User.user_id.distinct()).label('n_count'))
                .group_by(User.city)
                .order_by('n_count')).all()
        return dict(result)

    def _get_report(self):
        report_datetime = datetime.datetime.now()
        report = {
            'timestamp': str(report_datetime),
            'stats': self._get_user_count_by_city()
        }

        return report
