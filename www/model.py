#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Models for user, blog, comment."""

import time
import uuid
from ORM import Model, StringField, BooleanField, FloatField, TextField

__author__ = 'Wei'


# generate id by uuid
def next_id():
    # uuid4()randomly generate uuid,hex convert uuid from 32 bit to 64 bit
    return '%015d%s000' % (int(time.time() * 1000), uuid.uuid4().hex)


class User(Model):
    __table__ = 'users'
    # id is primary_key
    # default is used to save ids, next_id will be called if call insert
    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    email = StringField(ddl='varchar(50)')
    passwd = StringField(ddl='varchar(50)')
    admin = BooleanField()    # default value is false
    name = StringField(ddl='varchar(50)')
    image = StringField(ddl='varchar(500)')
    created_at = FloatField(default=time.time)

    def __init__(self, **kw):
        super(User, self).__init__(**kw)


class Blog(Model):
    __table__ = 'blogs'
    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    user_id = StringField(ddl='varchar(50)')
    user_name = StringField(ddl='varchar(50)')
    user_image = StringField(ddl='varchar(500)')
    name = StringField(ddl='varchar(50)')
    summary = StringField(ddl='varchar(200)')
    content = TextField()
    created_at = FloatField(default=time.time)

    def __init__(self, **kw):
        super(Blog, self).__init__(**kw)


class Comment(Model):
    __table__ = "comments"
    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    blog_id = StringField(ddl='varchar(50)')
    user_id = StringField(ddl='varchar(50)')
    user_name = StringField(ddl='varchar(50)')
    user_image = StringField(ddl='varchar(500)')
    content = TextField()
    created_at = FloatField(default=time.time)

    def __init__(self, **kw):
        super(Comment, self).__init__(**kw)


# u = User(id=12345, name='xxoo', email='test@gmail.com', password='my-pwd')
# u.save()
