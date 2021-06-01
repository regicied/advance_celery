import json
import traceback
from celery import Task
from redis import Redis
from celery_app import RESULT_POOL
from celery._state import _task_stack
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


class DBFreshBase(Task):
    #: Request class used, or the qualified name of one.
    Request = 'celeryFolder.taskModel.customer.db_refresh_request:DBRefreshRequest'

    def __call__(self, *args, **kwargs):
        request = self.request
        job_id = request.id
        db_session = SESSION()
        # the status of record always follows a linear change, so does not use the version
        try:
            db_session.query(RefreshTaskHistoryModel).filter(RefreshTaskHistoryModel.id == job_id).update(
                {'status': 'running'})
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

    # task success call back
    def on_success(self, retval, task_id, *args, **kwargs):
        logger.info(f'task id:{task_id}, arg:{args}, successful!')
        self._self_call_back(task_id, 'successful')

    # task failure call back
    def on_failure(self, exc, task_id, *args, **kwargs):
        logger.info(f'task id:{task_id}, arg:{args}, failed! erros:{exc}')
        self._self_call_back(task_id, 'failed')

    # task retry call back
    def on_retry(self, exc, task_id, *args, **kwargs):
        logger.info(f'task id:{task_id}, arg:{args}, retry! einfo:{exc}')

    def _self_call_back(self, task_id, status):
        rds = Redis(connection_pool=RESULT_POOL)
        db_session = SESSION()
        try:
            res = rds.get('celery-task-meta-%s' % task_id)
            res = json.loads(res)
            error = res['traceback']
            db_session.query(RefreshTaskHistoryModel).filter(RefreshTaskHistoryModel.id == task_id).update({
                'status': status,
                'error_info': error
            })
            db_session.commit()
            rds.delete('celery-task-meta-%s' % task_id)
        except Exception as e:
            db_session.rollback()
            raise e
            # TaskHistoryModel()
        finally:
            rds.close()
            db_session.close()
