import os
import sys
import datetime
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import(
    TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)
import random
import string

secret_key = ''.join(random.choice(
    string.ascii_uppercase + string.digits) for x in xrange(32))

Base = declarative_base()


class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    name = Column(String(250))


class ListItem(Base):
    __tablename__ = 'list_item'
    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(250))
    created_date = Column(DateTime, default=datetime.datetime.utcnow)
    category_id = Column(String(250), ForeignKey(
        'category.id'), nullable=False)
    category = relationship(Category)


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    email = Column(String(250))
    password_hash = Column(String(64))

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        print pwd_context.verify(password, self.password_hash)
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=600):
        s = Serializer(secret_key, expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(secret_key)
        try:
            data = s.loads(token)
        except SignatureExpired:
            # Valid Token, but expired
            return None
        except BadSignature:
            # Invalid Token
            return None
        user_id = data['id']
        return user_id


engine = create_engine('sqlite:///catalog.db')


Base.metadata.create_all(engine)
