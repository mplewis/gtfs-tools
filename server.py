import gtfs_utils

from flask import Flask, request
from flask_restful import Resource, Api, abort

import os


app = Flask(__name__)
if os.environ.get('TESTING'):
    app.config.from_object('config_test.Test')
elif os.environ.get('DEBUG'):
    app.config.from_object('config.Debug')
else:
    app.config.from_object('config.Base')


def get_static():
    config = app.config['GTFS_STATIC']
    if 'file' in config:
        return gtfs_utils.static_from_file(config['file'])
    print('Fetching static GTFS data from server. This may take a while...')
    return gtfs_utils.static_from_url(config['url'], **config['args'])


def get_realtime():
    config = app.config['GTFS_REALTIME']
    if 'file' in config:
        return gtfs_utils.realtime_from_file(config['file'])
    return gtfs_utils.realtime_from_url(config['url'], **config['args'])


ssched = get_static()


def get_route(route_id):
    try:
        return ssched.routes[route_id]
    except KeyError:
        abort(404, message='No route found with ID "{}"'.format(route_id))


def get_trip(trip_id):
    try:
        return ssched.trips[trip_id]
    except KeyError:
        abort(404, message='No trip found with ID "{}"'.format(trip_id))


def get_stop(stop_id):
    try:
        return ssched.stops[stop_id]
    except KeyError:
        abort(404, message='No stop found with ID "{}"'.format(stop_id))


def get_realtime_est(route_id, headsign, stop_id):
    rsched = get_realtime()
    get_route(route_id)
    trips = ssched.route_trips(route_id)
    trips = [t for t in trips if t['trip_headsign'] == headsign]
    if not trips:
        abort(404, message='No trips found with headsign "{}"'.format(headsign))
    get_stop(stop_id)
    return rsched.arrival_times(trips, stop_id)


def searchable(data, key):
    """
    Filter `data` on the case-insensitive value for `key` if the query
    parameter `q` is provided. Otherwise, return all data.
    """
    query = request.args.get('q')
    if query:
        return [i for i in data if query.lower() in i[key].lower()]
    return data


class Root(Resource):
    def get(self):
        return '', 204


class Routes(Resource):
    def get(self):
        return searchable(ssched.all_routes(), 'route_short_name')


class Route(Resource):
    def get(self, route_id):
        return get_route(route_id)


class Trips(Resource):
    def get(self, route_id):
        get_route(route_id)
        return searchable(ssched.route_trips(route_id), 'trip_headsign')


class Trip(Resource):
    def get(self, trip_id):
        return get_trip(trip_id)


class Stops(Resource):
    def get(self, trip_id):
        get_trip(trip_id)
        return searchable(ssched.trip_stops(trip_id), 'stop_name')


class Stop(Resource):
    def get(self, stop_id):
        return get_stop(stop_id)


class Realtime(Resource):
    def get(self):
        route_id = request.args.get('route')
        headsign = request.args.get('headsign')
        stop_id = request.args.get('stop')
        if not (route_id and headsign and stop_id):
            abort(400, message='Query params "route", "headsign", and "stop" are required')
        return get_realtime_est(route_id, headsign, stop_id)


api = Api(app)

api.add_resource(Root, '/')
api.add_resource(Routes, '/routes')
api.add_resource(Route, '/routes/<route_id>')
api.add_resource(Trips, '/routes/<route_id>/trips')
api.add_resource(Trip, '/trips/<trip_id>')
api.add_resource(Stops, '/trips/<trip_id>/stops')
api.add_resource(Stop, '/stops/<stop_id>')
api.add_resource(Realtime, '/realtime')


if __name__ == '__main__':
    app.run()
