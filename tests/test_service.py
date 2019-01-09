from nameko.testing.services import worker_factory
from temp_messenger.service import KonnichiwaService

def test_konnichiwa():
  service = worker_factory(KonnichiwaService)
  result = service.konnichiwa()
  assert result == 'Konnichiwa'