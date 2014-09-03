__author__ = 'Andrean'

from models import BaseModel
from models.contractor import Contractor
from bson.objectid import ObjectId
import defs
import schedule
import datetime
import time


class DataItem(BaseModel, defs.StoppableThread):

    StorageName = 'data_items'

    def __init__(self, item):
        BaseModel.__init__(self, item)
        defs.StoppableThread.__init__(self)
        self._scheduler = schedule.Scheduler()
        job = self._scheduler.every(self.schedule['interval'])
        job.unit = self.schedule['unit']
        if len(self.schedule['at']) > 0:
            job.at(self.schedule['at'][0])
        job.do(self.run_job)
        """
        data_item
            id: object_id,
            name: str,
            data_type: str,
            contractor: object_id,
            entity: object_id,
            schedule: {'interval': num, 'unit': str, 'at':[timestr]}
        """

    def run(self):
        while not self._stop_event.is_set():
            self._scheduler.run_pending()
            time.sleep(0.1)

    def run_job(self):
        contractor = self.contractor
        if contractor is None:
            self.send_error("Contractor {0} was not found".format(self._item.get('contractor')))
            return
        data = contractor.exec()
        self.send(data, contractor.hash)

    def send(self, data, hash):
        chunk = [dict(
            data_list=[dict(data=data,timestamp=datetime.datetime.now())],
            data_item=self.id,
            hash=hash
        )]
        self._client.send_data(chunk)

    def send_error(self, error):
        pass

    @property
    def id(self):
        return self._item.get('id')

    @property
    def schedule(self):
        return self._item.get('schedule')

    @property
    def contractor(self):
        _id = self._item.get('contractor')
        if not isinstance(_id, ObjectId):
            return None
        return Contractor.find(_id)

