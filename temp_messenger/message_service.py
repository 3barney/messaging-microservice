from nameko.rpc import rpc
from operator import itemgetter
from .dependencies.messages import MessageStore

class MessageService:

  name = 'message_service'
  message_store = MessageStore()

  @rpc
  def get_message(self, message_id):
    return self.message_store.get_message(message_id)

  @rpc
  def save_message(self, message):
    message_id = self.message_store.save_message(message=message)
    return message_id
  
  @rpc
  def get_all_messages(self):
    messages = self.message_store.get_all_messages()
    sorted_messages = sort_messages_by_expiry(messages)
    return sorted_messages


def sort_messages_by_expiry(messages, reverse=False):
  print(messages)
  return sorted(
    messages,
    key=itemgetter('expires-in'),
    reverse=reverse
  )
