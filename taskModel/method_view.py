from celery_app import celery_app
from taskModel.db_fresh.taskBase import DBFreshBase
from taskModel.db_fresh.job.dynamic_job import DynamicRefresh
from taskModel.db_fresh.job.static_job import StaticRefresh


# @celery_app.task(base=DBFreshBase)
# def demo_function(*args, **kwargs):
#     result = demo.Demo(*args, **kwargs).run(*args, **kwargs)
#     return result


@celery_app.task(base=DBFreshBase)
def dynamic_data_refresh(*args, **kwargs):
    result = DynamicRefresh.run(*args, **kwargs)
    return result


@celery_app.task(base=DBFreshBase)
def refresh_static_task(*args, **kwargs):
    result = StaticRefresh.run(*args, **kwargs)
    return result
