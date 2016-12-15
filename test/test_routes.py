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


def test_route():
    resp = app.get('/routes/BFC')
    resp.json['route_short_name'].should.equal('20')


def test_route_trips():
    resp = app.get('/routes/BFC/trips')
    len(resp.json).should.equal(2)


def test_route_trips_search():
    resp = app.get('/routes/BFC/trips?q=furnace')
    len(resp.json).should.equal(1)


def test_trip():
    resp = app.get('/trips/BFC1')
    resp.json['trip_headsign'].should.equal('to Furnace Creek Resort')


def test_trip_stops():
    resp = app.get('/trips/BFC1/stops')
    len(resp.json).should.equal(2)


def test_trip_stops_search():
    resp = app.get('/trips/BFC1/stops?q=bullfrog')
    len(resp.json).should.equal(1)
    resp.json[0]['stop_id'].should.equal('BULLFROG')
