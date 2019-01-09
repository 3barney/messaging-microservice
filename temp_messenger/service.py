from nameko.rpc import rpc, RpcProxy
# rpc allow decorate methonds with rpc  and expose them as entrypoints into our service.
from nameko.web.handlers import http


class KonnichiwaService:

  name = 'konnichiwa_service'

  @rpc
  def konnichiwa(self):
    return 'Konnichiwa'


class WebService:

  name = 'web_server'
  konnichiwa_service = RpcProxy('konnichiwa_service')

  @http('GET', '/')
  def home(self, request):
    return self.konnichiwa_service.konnichiwa()