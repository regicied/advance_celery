#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @File  : record_rm_handler.py
# @Author: gaofzhan
# @Email: gaofeng.a.zhang@ericssoin.com
# @Date  : 2021/2/22 12:51
# @Desc  :
from redis import Redis
from celery import Task
from celery._state import _task_stack
from celery_app import RESULT_POOL
from backend.myBluePrint.ericic_v2.mongo_post.record_post import RecordPost
from config import MONGO_DBNAME, MONGO_HOST, MONGO_NAME, MONGO_PASS, MONGO_PORT, MONGO_TIMEOUT
from mongoengine import connect as MONGO_CON
from mongoengine.connection import disconnect


class RecordDeleteObj:

    @classmethod
    def run(cls, cid):
        RecordPost.objects(cid=cid).delete()


class TaskBase(Task):

    def __call__(self, *args, **kwargs):
        URI = 'mongodb://{uname}:{pwd}@{host}:{port}/?authSource=admin'.format(uname=MONGO_NAME, pwd=MONGO_PASS,
                                                                               host=MONGO_HOST, port=MONGO_PORT)

        MONGO_CON(MONGO_DBNAME, host=URI, serverSelectionTimeoutMS=MONGO_TIMEOUT, connectTimeoutMS=MONGO_TIMEOUT,
                  socketTimeoutMS=MONGO_TIMEOUT)
        _task_stack.push(self)
        self.push_request(args=args, kwargs=kwargs)
        try:
            return self.run(*args, **kwargs)
        finally:
            self.pop_request()
            _task_stack.pop()
            disconnect()

    def on_success(self, retval, task_id, args, kwargs):
        rds = Redis(connection_pool=RESULT_POOL)
        try:
            rds.delete('celery-task-meta-%s' % task_id)
        finally:
            rds.close()
