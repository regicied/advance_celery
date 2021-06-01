#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @File  : method_view.py
# @Author: gaofzhan
# @Email: gaofeng.a.zhang@ericssoin.com
# @Date  : 2021/1/27 10:45
# @Desc  : 
from celery_app import celery_app
from optimus_executor.record_task.task_base import RecordTaskBase
from optimus_executor.record_task.gen_excel import gen2excel
from optimus_executor.post_rm_task.record_rm_handler import RecordDeleteObj, TaskBase


@celery_app.task(base=RecordTaskBase)
def gen_excel(*args, **kwargs):
    result = gen2excel(*args, **kwargs)
    return result


@celery_app.task(base=TaskBase)
def record_delete(*args, **kwargs):
    res = RecordDeleteObj.run(*args, **kwargs)
