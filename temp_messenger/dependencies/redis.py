from redis import StrictRedis
from nameko.extensions import DependencyProvider
from uuid import uuid4

class RedisClient:

  def __init__(self, url):
    self.redis = StrictRedis.from_url(url, decode_responses = True)

  def get_message(self, message_id):
    message = self.redis.get(message_id)

    if message is None:
      raise RedisError('Message not found: {}'.format(message_id))

    return message

  def save_message(self, message):
    message_id = uuid4().hex
    self.redis.set(message_id, message, ex=10)

    return message_id

  def get_all_messages(self):
    return [{
      'id': message_id,
      'message': self.redis.get(message_id),
      'expires-in': self.redis.pttl(message_id)
    } for message_id in self.redis.keys()]


# The dependency provider allow us to utilize the client(RedisClient) within our services
class MessageStore(DependencyProvider):

  def setup(self):
    redis_url = self.container.config['REDIS_URL']
    self.client = RedisClient(redis_url)

  def stop(self):
    del self.client

  def get_dependency(self, worker_ctx):
    return self.client

class RedisError(Exception):
  pass