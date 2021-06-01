import traceback
from celery import Task
from celery._state import _task_stack
from backend.Model.connection import SESSION, and_
from taskModel.db_fresh.taskBase import DBFreshBase
from backend.myBluePrint.ericic_v2.mongo_post.record_post import RecordPost
from backend.myBluePrint.ericic_v2.model.record import RecordModel


class Demo(Task):

    def __call__(self, *args, **kwargs):
        job_id = self.request.id
        db_session = SESSION()
        try:
            # record_status = db_session.query(RecordModel).filter(RecordModel.id == job_id).one_or_none()
            db_session.query(and_(RecordModel.id == job_id)).update({'status': 'running'})
            db_session.commit()
        except Exception:
            db_session.rollback()
            e = traceback.format_exc()
            print(e)
        finally:
            db_session.close()
        _task_stack.push(self)
        self.push_request(args=args, kwargs=kwargs)
        try:
            return self.run(*args, **kwargs)
        finally:
            self.pop_request()
            _task_stack.pop()

    def run(self, *args, **kwargs):
        job_id = None
        db_session = SESSION()
        try:
            record_status = db_session.query(RecordModel).filter(RecordModel.id == job_id).one_or_none()
            post = RecordPost()
            if db_session.query(RecordModel).filter(
                    and_(RecordModel.id == job_id, RecordModel.version == record_status.version)).update(
                {'version': record_status.version + 1}):
                post.save()
            db_session.commit()
        finally:
            db_session.close()

        return 'demo_success'

# demo_func = celery_app.task(Demo().run)
