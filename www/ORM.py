#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""ORM(object relational mapping), it map class to mySQL database
ORM connect to database, build cursor and have insert, execute. etc.."""

import asyncio, logging
import aiomysql

__author__ = 'Wei'


# printing SQL, log
def log(sql, args=()):
    logging.info('SQL: %s' % sql)

# build database connect pool, http request can get database data
@asyncio.coroutine
def creat_pool(loop, **kw):
    logging.info("create database connection pool...")
    global __pool
    # asyncronize build connection pool, return value of create_pool is pool instance
    __pool = yield from aiomysql.create_pool(
        # dict.get(key, default)
        host=kw.get("host", "localhost"),  # local database
        port=kw.get("port", 3306),  # mysql port
        user=kw["user"],  # user of mySQL
        password=kw["password"], # password
        db=kw["db"],  # database name
        charset=kw.get("charset", "utf8"),  # encode to utf-8
        autocommit=kw.get("autocommit", True),  # autocommit, the default value is false

        # the following setting is optional
        # max of pool, the default value is 10
        maxsize=kw.get("maxsize", 10),
        # min of pool, the default value is 10, here set to 1
        minsize=kw.get("minsize", 1),
        loop=loop
    )

# encapsulate select function of mySQL
@asyncio.coroutine
def select(sql, args, size=None):
    log(sql, args)
    global __pool
    # get a connection from connection pool
    with (yield from __pool) as conn:
        # open a DictCursor, it return a dictionary
        cur = yield from conn.cursor(aiomysql.DictCursor)
        # replace
        yield from cur.execute(sql.replace("?", "%s"), args or ())
        if size:
            rs = yield from cur.fetchmany(size)
        else:
            rs = yield from cur.fetchall()
        yield from cur.close()  # close cur
        logging.info("rows return %s" % len(rs))
        return rs


# delete, insert and update
@asyncio.coroutine
def execute(sql, args):
    log(sql)
    with (yield from __pool) as conn:
        if not conn.get_autocommit():
            yield from conn.begin()
    try:
        # ordinary cursor
        cur = yield from conn.cursor()
        yield from cur.execute(sql.replace("?", "%s"), args)
        affected = cur.rowcount  # row number
        yield from cur.close()  # over, close cursor
        if not conn.get_autocommit():
            yield from conn.commit()
    except BaseException as e:
        if not conn.get_autocommit(): # error happen, rollback
            yield from conn.rollback()
        raise
    return affected


def create_args_string(num):
    L = []
    for n in range(num):
        L.append("?")
    return ', '.join(L)


# Field class
class Field(object):
    # default parameter allow ORM fill in default value
    # eg. user has a id on StringField, default is used for storing user's id
    def __init__(self, name, column_type, primary_key, default):
        self.name = name
        self.column_type = column_type
        self.primary_key = primary_key
        self.default = default

    # print info:
    def __str__(self):
        return "<%s, %s:%s>" % (self.__class__.__name__, self.column_type, self.name)


# string field
class StringField(Field):
    # ddl("data definition languages"), define data type
    # varchar("variable char"), variable string; length of string 0~100
    def __init__(self, name=None, primary_key=False, default=None, ddl="varchar(100)"):
        super().__init__(name, ddl, primary_key, default)


# int field
class IntegerField(Field):
    def __init__(self, name=None, primary_key=False, default=0):
        super().__init__(name, "bigint", primary_key, default)


# bool field
class BooleanField(Field):
    def __init__(self, name=None, default=False):
        super().__init__(name, "boolean", False, default)


# float field
class FloatField(Field):
    def __init__(self, name=None, primary_key=False, default=0.0):
        super().__init__(name, "real", primary_key, default)


# text field
class TextField(Field):
    def __init__(self, name=None, default=None):
        super().__init__(name, "text", False, default)


# define metaclass
class ModelMetaclass(type):
    def __new__(cls, name, bases, attres):
        # cls: class object
        # name: class name, if user is heirage of Model, when we use metaclass, name = User
        # bases: 元祖
        # attrs: attributes (dict), eg. User has __table__, id
        if name == "Model":
            return type.__new__(cls, name, bases, attrs)


        # we only deal with module child class,

        tableName = attrs.get("__table__", None) or name
        logging.info("found model: %s (table: %s)" % (name, tableName))
        # get all Field
        mappings = dict()   # keep mapping info of class attrs and database table
        fields = []         # keep attrs except primaryKey
        primaryKey = None   # keep primaryKey

        # k is attrs; v is Field name=StringField(ddl="varchar50")
        for k, v in attrs.items():
            if isinstance(v, Field):
                logging.info("found mapping: %s ==> %s" % (k, v))
                mappings[k] = v  # build mapping info
                if v.primary_key:
                    if primaryKey:
                        raise RuntimeError("Duplicate primary key for field: %s" % s)
                    primaryKey = k
                else:
                    fields.append(k)
        if not primaryKey:
            raise RuntimeError("Primary key not found")
        for k in mapping.keys():
            attrs.pop(k)
        # 将非主键的属性变形,放入escaped_fields中,方便增删改查语句的书写
        escaped_fields = list(map(lambda f: "`%s`" % f, fields))
        attrs["__mappings__"] = mappings  # save the mapping info
        attrs["__table__"] = tableName  # same table name
        attrs["__primary_key__"] = primaryKey  # save primary key
        attrs["__fields__"] = fields

        # construct select, insert, update, delete
        attrs["__select__"] = "select `%s`, %s from `%s`" % (primaryKey, ', '.join(escaped_fields), tableName)
        # 此处利用create_args_string生成的若干个?占位
        attrs["__insert__"] = "insert into `%s` (%s, `%s`) values (%s)" % (
        tableName, ', '.join(escaped_fields), primaryKey, create_args_string(len(escaped_fields) + 1))
        attrs["__update__"] = "update `%s` set %s where `%s`=?" % (
        tableName, ', '.join(map(lambda f: "`%s`=?" % (mappings.get(f).name or f), fields)), primaryKey)
        attrs["__delete__"] = "delete from `%s` where `%s`=?" % (tableName, primaryKey)
        return type.__new__(cls, name, bases, attrs)


# model metaclass
class Model(dict, metaclass=ModelMetaclass):
    def __init__(self, **kw):
        super(Model, self).__init__(**kw)

    # "a.b"
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Model' object has no attribute'%s'" % key)

    # "a.b=c"
    def __setattr__(self, key, value):
        self[key] = value

    def getValue(self, key):
        return getattr(self, key, None)

    def getValueOrDefault(self, key):
        value = getattr(self, key, None)
        if value is None:
            field = self.__mappings__[key]
            if field.default is not None:
                # StringField.default=next_id, get id
                # FloatField.default=time.time, get time
                value = field.default() if callable(field.default) else field.default
                logging.debug("using default value for %s: %s" % (key, str(value)))
                setattr(self, key, value)
        return value

# 对于查询相关的操作,我们都定义为类方法,就可以方便查询,而不必先创建实例再查询
@classmethod
@asyncio.coroutine
def find(cls, pk):
    'find object by primary key'
    rs = yield from select("%s where `%s`=?" % (cls.__select__, cls.__primary_key__), [pk], 1)
    if len(rs) == 0:
        return None
    # select open DictCursor, return dict
    return cls(**rs[0])

@classmethod
@asyncio.coroutine
def findAll(cls, where=None, args=None, **kw):
    sql = [cls.__select__]
    if where:
        sql.append("where")
        sql.append(where)
    if args is None:
        args = []
    orderBy = kw.get("orderBy", none)
    if orderBy:
        sql.append("order by")
        sql.append(orderBy)
    limit = kw.get("limit", None)
    if limit is not None:
        sql.append("limit")
        if isinstance(limit, int):
            sql.append("?")
            args.append(limit)
        elif isinstance(limit, tuple) and len(limit) == 2:
            sql.append("?, ?")
            args.extend(limit)
        else:
            raise ValueError("Invalid limit value: %s" % str(limit))
    rs = yield from select(' '.join(sql), args)  # fetchall
    return [cls(**r) for r in rs]


@classmethod
@asyncio.corountine
def findNumber(cls, selectField, where=None, args=None):
    sql = ["select %s _num_from `%s`" % (selectField, cls.__table__)]
    if where:
        sql.append("where")
        sql.append(where)
    rs = yield from select(' '.join(sql), args, 1)
    if len(rs) == 0:
        return None
    return rs[0]["_num_"]


@asyncio.coroutine
def save(self):
    # append primary_key
    args = list(map(self.getValueOrDefault, self.__fields__))  # time.time get value
    args.append(self.getValueOrDefault(self.__primary_key__))
    rows = yield from execute(self.__insert__, args)
    if rows != 1:
        logging.warn("failed to insert record: affected row: %s" % rows)


@asyncio.corountine
def update(self):
    args = list(map(self.getValue, self.__field__))
    args.append(self.getValue(self.__primary_key__))
    rows = yield from execute(self.__update__, args)
    if rows != 1:
        logging.warn("failed to update by primary key: affected rows %s" % rows)


@asyncio.coroutine
def remove(self):
    args = [self.getValue(self.__primary_key__)]
    rows = yield from execute(self.__delete__, args)
    if rows != 1:
        logging.warn("failed to remove by primary key: affected rows %s" % rows)
