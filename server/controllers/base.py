__author__ = 'Andrean'


def get_404( req, res ):
    res.send_error(404)


def get_500(res):
    res.send_error(500)