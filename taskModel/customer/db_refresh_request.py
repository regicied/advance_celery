#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @File  : db_refresh_request.py
# @Author: gaofzhan
# @Email: gaofeng.a.zhang@ericssoin.com
# @Date  : 2021/2/25 14:05
# @Desc  :
from backend.Model.connection import SESSION
from backend.myBluePrint.ericic_v2.model.record_table import Record
from celery.worker.request import Request, state
from celery.utils.log import get_logger

logger = get_logger(__name__)
debug, info, warn, error = (logger.debug, logger.info, logger.warning, logger.error)
revoked_tasks = state.revoked


class DBRefreshRequest(Request):

    def revoked(self):
        """If revoked, skip task and mark state."""
        expired = False
        if self._already_revoked:
            return True
        if self._expires:
            expired = self.maybe_expire()
        if self.id in revoked_tasks:
            db_session = SESSION()
            try:
                db_session.query(Record).filter(Record.id == self.id).update({'status': 'revoked',
                                                                              'traceback': 'task had been expired'})
                db_session.commit()
            except Exception as e:
                db_session.rollback()
                info(e)
            finally:
                db_session.close()
            info('Discarding revoked task: %s[%s]', self.name, self.id)
            self._announce_revoked(
                'expired' if expired else 'revoked', False, None, expired,
            )
            return True
        return False
