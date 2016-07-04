from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declared_attr
from passlib.hash import sha256_crypt
import datetime
import logging
import uuid

LOG = logging.getLogger()

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    ID =  Column(Integer, primary_key=True)
    name = Column(String)
    password_hash = Column(String)
    public_attrs = [
        name,
    ]

    def __init__(self, session=None):
        pass

    def __repr__(self):
        return "<User(name='{0}')>".format(self.name)

    def generate_hash(self, password):
        """Generate a salted password hash for the new password password
        Do NOT use this to verify passwords. The salt will be different
        and it won't work at all.
        :param password: The cleartext password to be hashed
        :type password: (str.)
        :return: (str.) the password hash to store
        """
        return sha256_crypt.encrypt(password)

    def login(self, password):
        """Check if the password matches this user
        :param password: The cleartext password to be checked
        :type password: (str.)
        :return: (bool.) True if password matches, else false
        """
        return sha256_crypt.verify(password, self.password_hash)

class WebSession(Base):
    __tablename__ = 'sessions'
    ID =  Column(Integer, primary_key=True)
    name = Column(String)
    user_id = Column(Integer, ForeignKey('users.ID'))
    user = relationship("User")
    timestamp = Column(DateTime)
    uuid = Column(String)

    def __init__(self, user_id):
        self.user_id = user_id
        self.timestamp = datetime.datetime.now()
        self.uuid = str(uuid.uuid4())

    def __repr__(self):
        return "<Session(ID='{0}', user='{1}', time='{2}'>".format(self.ID, self.user_id, self.timestamp)

