import sys
import celery_config
from celery import Celery
from redis import ConnectionPool

sys.path.append('../')


RESULT_POOL = ConnectionPool(host=REDIS_HOST, password=REDIS_PASS, port=REDIS_PORT, decode_responses=True, db=15)

INCLUDE = [
    'optimus_executor.method_view',
    'taskModel.method_view'
]

TASK_ROUTES = {
    'optimus_executor.method_view.*': {'queue': 'optimus_worker'},
    'taskModel.method_view.*': {'queue': 'db_refresh'},
}

TASK_QUEUES = {
    "optimus_worker": {
        "exchange": "optimus_worker"
    },
    "db_refresh": {
        "exchange": "db_refresh"
    }
}

celery_app = Celery(__name__, include=INCLUDE)
celery_app.config_from_object(celery_config)
celery_app.conf.update(task_routes=TASK_ROUTES, task_queues=TASK_QUEUES)

# celery_app.autodiscover_tasks()
# revoke(id, terminate=True)
# update_state
