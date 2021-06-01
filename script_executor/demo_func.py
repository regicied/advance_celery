#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @File  : demo_func.py
# @Author: gaofzhan
# @Email: gaofeng.a.zhang@ericssoin.com
# @Date  : 2021/1/27 10:44
# @Desc  :
import time
from backend.Model.connection import SESSION
from backend.Model.UserModel import User
from celery_app import celery_app


@celery_app.task
def demo_func(job_id, uname):
    print('demo_func start', 'job_id --> ', job_id)
    db_session = SESSION()
    try:
        res = db_session.query(User).filter(User.name == uname).one_or_none()
        time.sleep(5)
        if res:
            print(res.name)
        else:
            print('None')

    finally:
        # update job statue running --> success
        db_session.close()

    # return dict(res='success')
