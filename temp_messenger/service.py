from nameko.rpc import rpc # allow decorate methonds with rpc  and expose them as entrypoints into our service.

class KonnichiwaService:

  name = 'konnichiwa_service'

  @rpc
  def konnichiwa(self):
    return 'Konnichiwa'