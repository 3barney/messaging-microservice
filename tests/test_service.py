from mock import patch
from time import sleep

import pytest
from fakeredis import FakeStrictRedis
from nameko.containers import ServiceContainer
from nameko.testing.services import entrypoint_hook

from temp_messenger.dependencies.redis import RedisError
from temp_messenger.service import (
  MessageService,
  WebService
)

from nameko.testing.services import worker_factory
from temp_messenger.service import KonnichiwaService

@pytest.fixture
def fake_strict_redis():
  with patch(
    'temp_messenger.dependencies.redis.StrictRedis', FakeStrictRedis
    ) as fake_strict_redis:
      yield fake_strict_redis
      fake_strict_redis().flushall()


@pytest.fixture
def config(web_config):
  return dict(
    AMQP_URI='pyamqp://guest:guest@localhost',
    REDIS_URL='redis://redis:6379/0',
    **web_config,
  )

@pytest.fixture
def uuid4():
  with patch('temp_messenger.dependencies.redis.uuid4') as uuid4:
    yield uuid4

@pytest.fixture
def message_svc(config, fake_strict_redis):
  message_svc = ServiceContainer(MessageService, config)
  message_svc.start()
  
  return message_svc

@pytest.fixture
def web_server(config, fake_strict_redis):
  web_server = ServiceContainer(WebService, config)
  web_server.start()

  return web_server

@pytest.fixture
def message_lifetime():
  with patch('temp_messenger.dependencies.redis.MESSAGE_LIFETIME', 100) as lifetime:
    yield lifetime


def test_homepage(web_server, message_svc, web_session, fake_strict_redis):
  result = web_session.get('/')
  assert 200 == result.status_code
  assert '<!DOCTYPE html>' in result.text
  # assert 'TempMessenger' in result.text

def test_get_messages(message_svc, fake_strict_redis):
  fake_strict_redis().set('msg1', 'Test message here')

  with entrypoint_hook(message_svc, 'get_message') as get_message:
    message = get_message('msg1')

  assert message == 'Test message here'

def test_raises_error_if_no_message_exists(message_svc, fake_strict_redis):
  with entrypoint_hook(message_svc, 'get_message') as get_message:
    with pytest.raises(RedisError) as err:
      get_message('message_non')
  
  err.match(r'Message not found: message_non')

def test_saves_new_message(message_svc, fake_strict_redis, uuid4):
  uuid4.return_value.hex = 'abcdef123456'

  with entrypoint_hook(message_svc, 'save_message') as save_message:
    message_id = save_message('Test message here')

  assert message_id == 'abcdef123456'
  # Writing point:
  # When first running this, it will fail since the message is
  # in bytes. fake_strict_redis is not set up to
  # decode_responses. decode() is needed
  message = fake_strict_redis().get('abcdef123456').decode()
  assert message == 'Test message here'


def test_gets_all_messages(message_svc, fake_strict_redis):
  fake_strict_redis().set('message-1', 'Hello')
  fake_strict_redis().set('abcdef123456', 'Howdy')
  fake_strict_redis().set('xyz789', 'I Love Python')
  fake_strict_redis().set('aaaabbbb', 'So do I!')

  with entrypoint_hook(
    message_svc, 'get_all_messages'
  ) as get_all_messages:
    messages = get_all_messages()

  assert messages == [
    {'id': 'message-1', 'message': 'Hello', 'expires_in': -1},
    {'id': 'abcdef123456', 'message': 'Howdy', 'expires_in': -1},
    {'id': 'xyz789', 'message': 'I Love Python', 'expires_in': -1},
    {'id': 'aaaabbbb', 'message': 'So do I!', 'expires_in': -1},
  ]


def test_returns_empty_list_if_no_messages(message_svc):
  # Writing point:
  # This test will fail at first since redis is not cleared
  # after each test. Explain the tear down
  with entrypoint_hook(
    message_svc, 'get_all_messages'
  ) as get_all_messages:
    messages = get_all_messages()

  assert messages == []