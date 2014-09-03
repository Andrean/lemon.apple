from unittest import TestCase
import unittest
from models.contractor import Contractor
import bson.objectid
import os
import hashlib
import core, config, modules

__author__ = 'Andrean'


class TestContractor(TestCase):

    @classmethod
    def setUpClass(cls):
        cfg = config.Config()
        cfg.Load('conf/agent.yaml')
        cfg.LoadLogging('conf/logging.yaml')
        c = core.Core(cfg)
        c.add(modules.storage.Storage)
        c.add(modules.client.Client)
        c.start()
        cls.c = c

    def setUp(self):
        self.contractor_meta_simple = dict(
            id=bson.objectid.ObjectId(),
            name='test1',
            type='py',
            args=['lol']
        )
        self.contractorSimple = Contractor(self.contractor_meta_simple)
        self.contractorSimple.save()
        self.contractor_meta_second = dict(
            id=bson.objectid.ObjectId(),
            name='test2',
            type='py',
            args=[]
        )
        self.contractorSecond = Contractor(self.contractor_meta_second)
        self.contractorSecond.save()

    def tearDown(self):
        self.contractorSimple.delete()
        self.contractorSecond.delete()

    def test_EmptyInit(self):
        c = Contractor()
        self.assertIsInstance(c._item, dict)

    def test_InitFromStorage(self):
        contractor_meta = dict(
            id=bson.objectid.ObjectId(),
            name='test1',
            type='py',
            args=['lol']
        )
        c = Contractor(contractor_meta)
        self.assertIsInstance(c._item, dict)
        self.assertEqual(c._item['id'],contractor_meta['id'])
        self.assertEqual(c._item['name'], contractor_meta['name'])
        self.assertListEqual(c._item['args'], contractor_meta['args'])

    def test_InitWithData(self):
        contractor_data = dict(
            id=bson.objectid.ObjectId(),
            name='test1',
            type='py',
            args=['lol'],
            data=bytes("print('something')", "utf8")
        )
        c = Contractor(contractor_data)
        c.save()
        self.assertTrue(os.path.exists(c.path))
        c.delete()

    @unittest.skip
    def test_exec_TimeoutExpired(self):
        contractor_script = """import time
while True:
    print("I am working")
    time.sleep(1)"""
        contractor_data = dict(
            id=bson.objectid.ObjectId(),
            name='test2',
            type='py',
            args=[],
            data=bytes(contractor_script, "utf8")
        )
        c = Contractor(contractor_data)
        result = c.exec()
        self.assertDictEqual(result,dict(error="timeout expired"))

    def test_exec(self):
        contractor_data = dict(
            id=bson.objectid.ObjectId(),
            name='test1',
            type='py',
            args=[],
            data=bytes("print('{0}')".format('{"result": 112}'), "utf8")
        )
        c = Contractor(contractor_data)
        c.save()
        result = c.exec()
        self.assertIsInstance(result, dict)
        self.assertDictEqual(result, dict(result=112))
        c.delete()

    def test_save(self):

        contractor_data = dict(
            id=bson.objectid.ObjectId(),
            name='test1',
            type='py',
            args=[],
            data=bytes("print('{0}')".format('{"result": 112}'), "utf8")
        )
        c = Contractor(contractor_data)
        c.save()
        self.assertTrue(os.path.exists(c.path))
        c.delete()

    def test_delete(self):
        contractor_data = dict(
            id=bson.objectid.ObjectId(),
            name='test1',
            type='py',
            args=['lol'],
            data=bytes("print('something')", "utf8")
        )
        c = Contractor(contractor_data)
        c.save()
        path = c.path
        c.delete()
        self.assertFalse(os.path.exists(path))

    def test_id(self):
        self.assertIsInstance(self.contractorSimple.id, bson.objectid.ObjectId)
        self.assertEqual(self.contractor_meta_simple['id'], self.contractorSimple.id)
        self.assertEqual(self.contractor_meta_second['id'], self.contractorSecond.id)

    def test_name(self):
        self.assertIsInstance(self.contractorSimple.name, str)
        self.assertEqual(self.contractor_meta_simple['name'], self.contractorSimple.name)
        self.assertEqual(self.contractor_meta_second['name'], self.contractorSecond.name)

    def test_path(self):
        self.assertIsInstance(self.contractorSimple.path, str)

    def test_type(self):
        self.assertIsInstance(self.contractorSimple.type, str)
        self.assertEqual(self.contractor_meta_simple['type'], self.contractorSimple.type)
        self.assertEqual(self.contractor_meta_second['type'], self.contractorSecond.type)

    def test_args(self):
        self.assertIsInstance(self.contractorSimple.args, list)
        self.assertIsInstance(self.contractorSecond.args, list)
        self.assertEqual(self.contractor_meta_simple['args'], self.contractorSimple.args)
        self.assertEqual(self.contractor_meta_second['args'], self.contractorSecond.args)

    def test_hash(self):
        contractor_data = dict(
            id=bson.objectid.ObjectId(),
            name='test1',
            type='py',
            args=['lol'],
            data=bytes("print('something')", "utf8")
        )
        m = hashlib.md5()
        m.update(bytes("print('something')", "utf8"))
        c = Contractor(contractor_data)
        c.save()
        self.assertEqual(c.hash, m.hexdigest())
        c.delete()

    @classmethod
    def tearDownClass(cls):
        cls.c.stop()
        del(cls.c)
