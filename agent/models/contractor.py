__author__ = 'Andrean'


from models import BaseModel
import os
import subprocess
import hashlib
import json
import bson.json_util
import traceback
import sys


class Contractor(BaseModel):

    StorageName = 'contractors'
    Directory = './contractors'

    def __init__(self, item=None):
        super().__init__(item)
        self._item['hash'] = None
        self._set_exec()
        os.makedirs(self.Directory, exist_ok=True)

    def save(self):
        super().save()
        self._item['path'] = os.path.join(
            os.path.abspath(self.Directory),
            "{0}.{1}.{2}".format(str(self.id), self.name, self.type)
        )
        if 'data' in self._item:
            with open(self.path, 'wb') as f:
                f.write(self._item.get('data'))
                self._item.pop('data')

    def delete(self):
        if self.id in self.Instances:
            super().delete()
            if os.path.exists(self.path):
                os.remove(self.path)

    def kill(self):
        """
        Kill all running instances of that contractor
        :return:
        """
        pass

    def exec(self, _args=[]):
        """
        Process returns JSON string. Contractor returns object of this JSON
        :param _args:
        :return: dict object
        """
        if os.path.exists(self.path) is not True:
            return
        process = self._exec(_args)
        try:
            outs, err = process.communicate(timeout=20)
        except subprocess.TimeoutExpired:
            process.kill()
            _, _ = process.communicate()
            return dict(error="timeout expired")
        except:
            return dict(error=''.join(traceback.format_exception(*(sys.exc_info()))))
        if process.returncode != 0:
            return dict(error="return code: {0}".format(process.returncode),msg=outs)
        try:
            result = json.loads(outs.strip(), encoding=sys.getdefaultencoding(), object_hook=bson.json_util.object_hook)
        except:
            result=dict(error="wrong format")
        finally:
            return result

    def _set_exec(self):
        if self.type == 'py':
            self._exec = self._exec_python

    def _exec(self, _args):
        raise NotImplementedError("Exec method not implemented")

    def _exec_python(self, _args):
        args = [sys.executable, self.path]
        args.extend(_args)
        process = subprocess.Popen(
                args=args,
                universal_newlines=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
        return process

    @property
    def id(self):
        return self._item.get('id')

    @property
    def name(self):
        return self._item.get('name')

    @property
    def path(self):
        return self._item.get('path')

    @property
    def type(self):
        return self._item.get('type')

    @property
    def args(self):
        return self._item.get('args')

    @property
    def hash(self):
        with open(self.path, 'rb') as f:
            self._item['hash'] = hashlib.md5(f.read()).hexdigest()
        return self._item.get('hash')



