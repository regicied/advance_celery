#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @File  : taskBase.py
# @Author: gaofzhan
# @Email: gaofeng.a.zhang@ericssoin.com
# @Date  : 2021/2/3 16:14
# @Desc  : 
# import json
import traceback
from redis import Redis
from celery import Task
from celery._state import _task_stack
from celery_app import RESULT_POOL
from celery.utils.log import get_task_logger


logger = get_task_logger(__name__)


class RecordTaskBase(Task):

    def __call__(self, *args, **kwargs):
        request = self.request
        job_id = request.id
        # db_session = SESSION()
        # URI = 'mongodb://{uname}:{pwd}@{host}:{port}/?authSource=admin'.format(uname=MONGO_NAME, pwd=MONGO_PASS,
        #                                                                        host=MONGO_HOST, port=MONGO_PORT)

        # MONGO_CON(MONGO_DBNAME, host=URI, serverSelectionTimeoutMS=MONGO_TIMEOUT, connectTimeoutMS=MONGO_TIMEOUT,
        #           socketTimeoutMS=MONGO_TIMEOUT)
        # the status of record always follows a linear change, so does not use the version
        try:
            db_session.query(Record).filter(Record.id == job_id).update({'status': 'running'})
            db_session.commit()
        except:
            db_session.rollback()
            msg = traceback.format_exc()
            logger.info(msg)
        finally:
            db_session.close()
        _task_stack.push(self)
        self.push_request(args=args, kwargs=kwargs)
        try:
            return self.run(*args, **kwargs)
        finally:
            self.pop_request()
            _task_stack.pop()
            disconnect()

    # task success call back
    def on_success(self, retval, task_id, *args, **kwargs):
        logger.info(f"task id:{task_id}, arg:{args}, successful!")
        self._self_call_back(task_id, 'successful', retval)

    # task failure call back
    def on_failure(self, exc, task_id, *args, **kwargs):
        logger.info(f"task id:{task_id}, arg:{args}, failed! erros:{exc}")
        self._self_call_back(task_id, 'failed', None)

    # task retry call back
    def on_retry(self, exc, task_id, *args, **kwargs):
        logger.info(f"task id:{task_id}, arg:{args}, retry! einfo:{exc}")

    def _self_call_back(self, task_id, status, post_id, exc=None):
        db_session = SESSION()
        rds = Redis(connection_pool=RESULT_POOL)
        try:
            if db_session.query(Record).filter(Record.id == task_id).update(
                    {'status': status, 'pid': post_id, 'traceback': exc}):
                rds.delete('celery-task-meta-%s' % task_id)
            db_session.commit()
        except Exception as e:
            db_session.rollback()
            raise e
        finally:
            rds.close()
            db_session.close()
