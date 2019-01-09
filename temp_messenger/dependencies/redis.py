from redis import StrictRedis

class RedisClient:

  def __init__(self, url):
    self.redis = StrictRedis.from_url(url, decode_responses = True)

  def get_message(self, message_id):
    message = self.redis.get(message_id)

    if message is None:
      raise RedisError('Message not found: {}'.format(message_id))

    return message


class RedisError(Exception):
  pass