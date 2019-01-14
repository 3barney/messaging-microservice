import bcrypt
from sqlalchemy import Column, Integer, Unicode, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from nameko_sqlalchemy import DatabaseSession

HASH_WORK_FACTOR = 15

Base = declarative_base() # create mapping btwn User Model and db table

class User(Base):
  __tablename__ = 'users'

  id = Column(Integer, primary_key=True)
  first_name = Column(Unicode(length=128))
  last_name = Column(Unicode(length=128))
  email = Column(Unicode(length=128), unique=True)
  password = Column(LargeBinary())


# a wrapper class that will be used to encapsulate all of the logic around
# managing users.
class UserWrapper:

  # Require a db session object
  def __init__(self, session):
    self.session = session


  # **kwargs instead of defining the actual arguments to create a new User . If we were to change the user model,
  # this minimizes the changes needed since the keyword arguments directly map to the fields.
  def create(self, **kwargs):
    plain_text_password = kwargs['password']
    hashed_password = hash_password(plain_text_password)
    kwargs.update(password=hashed_password)

    user = User(**kwargs)
    self.session.add(user)
    self.session.commit()


# User Store, which will serve as our dependency:
class UserStore(DatabaseSession): # DatabaseSession has the dependencies such as set_up() get_dependency()

  def __init__(self):
    super().__init__(Base)

  def get_dependency(self, worker_ctx):
    database_session = super().get_dependency(worker_ctx)
    return UserWrapper(session=database_session)
    # The original get_dependency method in the DatabaseSession class simply returns a
    # database session; however, we want ours to return an instance of our UserWrapper


def hash_password(plain_text_password):
  salt = bcrypt.gensalt(rounds=HASH_WORK_FACTOR)
  encoded_password = plain_text_password.encode()

  return bcrypt.hashpw(encoded_password, salt)