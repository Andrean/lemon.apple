import unittest
from unittest import TestCase
from bson.objectid import ObjectId
from models.contractor import Contractor
from models.data_item import DataItem
import time
import modules
import core, config,bson.json_util

__author__ = 'Andrean'


class TestDataItem(TestCase):

    def setUp(self):

        contractor_data = dict(
            id=bson.objectid.ObjectId(),
            name='test1',
            type='py',
            args=[],
            data=bytes("print('{0}')".format('{"result": 112}'), "utf8")
        )
        self.contractor = Contractor(contractor_data)
        self.contractor.save()

        self.data_item_test = dict(
            name="first_data_item",
            entity=ObjectId(),
            contractor=self.contractor.id,
            data_type='number',
            id=ObjectId(),
            schedule=dict(interval=1,unit='seconds',at=[])
        )


    # def test_run(self):
    #     item = DataItem(self.data_item_test)
    #     item.start()
    #     time.sleep(10)
    #     item.stop()

    #@unittest.skip
    def test_run_job(self):
        c = core.Core.Instance
        c.start()

        item = DataItem(self.data_item_test)
        item.save()
        item.start()
        time.sleep(10)
        item.stop()
        item.delete()
        c.stop()
        del(c)

    def test_id(self):
        item = DataItem(self.data_item_test)
        self.assertEqual(item.id, self.data_item_test['id'])

    def test_schedule(self):
        item = DataItem(self.data_item_test)
        self.assertDictEqual(self.data_item_test['schedule'], item.schedule)

    def tearDown(self):
        self.contractor.delete()
