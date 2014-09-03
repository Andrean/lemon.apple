__author__ = 'Andrean'

import models.contractor


def add_or_modify(req):
    if len(req.command.args) > 0:
        contractor_data = req.command.args[0]
        contractor = models.contractor.Contractor(contractor_data)
        contractor.save()
        req.set_completed(dict(path=contractor.path))


def delete(req):
    if len(req.command.args) > 0:
        contractor_oid = req.command.args[0]
        c = models.contractor.Contractor.find(contractor_oid)
        if c is not None:
            c.delete()
            req.set_completed(dict(status=True))


def run(req):
    pass


def kill(req):
    pass

