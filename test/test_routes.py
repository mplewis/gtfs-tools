from server import app as app_under_test

import sure  # noqa
from webtest import TestApp as TApp


app = TApp(app_under_test)


def test_root():
    app.get('/', status=204)


def test_routes():
    resp = app.get('/routes')
    len(resp.json).should.equal(5)


def test_route_search():
    resp = app.get('/routes?q=2')
    len(resp.json).should.equal(1)
    name = resp.json[0]['route_long_name']
    name.should.equal('Bullfrog - Furnace Creek Resort')
