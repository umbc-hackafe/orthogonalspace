from sqlalchemy import *
from sqlalchemy.orm import sessionmaker, scoped_session
import os
from passlib.hash import sha256_crypt
import datetime
import random
import string
import logging
import enum
from sqlalchemy.ext.declarative import declarative_base
from orthogonalspace.types import *
import orthogonalspace.types

LOG = logging.getLogger()

class Database:
    def __init__(self, config):
        """Initialize the database connection and create missing tables.
        This will also initialize the admin user if it doesn't exist already.
        The configuration is the same dictionary defined in the conf.json
        :param config: The configuration for the database
        :param type: (dict.)
        """
        self.config = config

        Base = orthogonalspace.types.Base
        db = create_engine(self.config['db_uri'], echo=False)
        Base.metadata.create_all(db)
        self.Session = sessionmaker(bind=db)

    def add_user(self, username, password):
        session = self.Session()
        user = User()
        user.name = username
        user.password_hash = user.generate_hash(password)
        session.add(user)
        session.commit()

    def verify_hash(self, password, password_hash):
        """Verify that the cleartext password matches the supplied hash
        :param password: The cleartext password to be hashed
        :type password: (str.)
        :param password_hash: The hash, including salt, as supplied by generate_hash()
        :type password_hash: (str.)
        :return: (bool.) True if the hash matches, otherwise false
        """
        return sha256_crypt.verify(password, password_hash)

    def login(self, username, password):
        """Attempt to log in the given user.
        :param username: The name of the user to log in
        :type username: (str.)
        :param password: The cleartext password of the user to log in
        :type password: (str.)
        :return: (int./bool.) session_id if the login succeeded, otherwise False
        """
        session = self.Session()
        user = session.query(User).filter(User.name == username).first()
        if user:
            if verify_hash(password, user.password_hash):
                webSession = WebSession(user.user_id)
                session.add(webSession)
                session.commit()
                return webSession.session_id
        else:
            return False

    def check_session(self, session_id, user_id):
        """Verify that the given session is still valid for the user.
        Sessions by default will time out after a number of seconds defined in
        conf.json as "session_duration". They will reset the timeout on every
        valid pageload if "keep_session_alive" is True.
        :param session_id: The id of the session as set in a user cookie
        :type session_id: (int.)
        :param user_id: The id of the user whose session is being verified
        :type user_id: (int.)
        :return: (bool.) True if the session is valid, otherwise false.
        """
        current_time = datetime.datetime.today()
        session_duration = self.config['session_duration']
        session = self.Session()
        webSessions = session.query(WebSession).filter(WebSession.user_id == user_id).all()

        success = False
        delete = []
        for webSession in webSession:
            if (current_time - webSession.timestamp).total_seconds() > session_duration:
                delete.append(webSession)
            elif session_id == webSession.session_id:
                if self.config['keep_session_alive']:
                    webSession.timestamp = current_time
                    session.commit()
                success = True

        for i in delete:
            session.delete(i)
        session.commit()

        return success
