from nameko.rpc import rpc, RpcProxy # rpc allow decorate methonds with rpc  and expose them as entrypoints into our service.
from nameko.web.handlers import http
from werkzeug.wrappers import Response
import json

from .dependencies.redis import MessageStore
from .dependencies.jinja2 import Jinja2

class WebService:

  name = 'web_server'
  message_service = RpcProxy('message_service')
  templates = Jinja2()
  
  @http('GET', '/')
  def home(self, request):
    messages = self.message_service.get_all_messages()
    rendered_template = self.templates.render_home(messages)
    html_response = create_html_response(rendered_template)

    return html_response

  @http('POST', '/messages')
  def post_message(self, request):
    data_as_text = request.get_data(as_text = True)

    try:
      data = json.loads(data_as_text)
    except json.JSONDecodeError:
      return 400, 'JSON payload expected'

    try:
      message = data['message']
    except KeyError:
      return 400, 'No message given'

    self.message_service.save_message(message)

    return 204, ''


class MessageService:

  name = 'message_service'
  message_store = MessageStore()

  @rpc
  def get_message(self, message_id):
    return self.message_store.get_message(message_id)

  @rpc
  def save_message(self, message):
    message_id = self.message_store.save_message(message)
    return message_id

  @rpc
  def get_all_messages(self):
    messages = self.message_store.get_all_messages()
    return messages


# Use this to Format html Response
def create_html_response(content):
  headers = {'Content-type': 'text/html'}
  return Response(content, status=200, headers=headers)