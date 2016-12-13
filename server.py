import gtfs_utils
from config import rtd_creds

from flask import Flask, request
from flask_restful import Resource, Api, abort
from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options

realtime_url = 'http://www.rtd-denver.com/google_sync/TripUpdate.pb'

gtfs_cache = CacheManager(**parse_cache_config_options({
    'cache.type': 'file',
    'cache.data_dir': '/tmp/gtfs-tools/data',
    'cache.lock_dir': '/tmp/gtfs-tools/lock',
}))

@gtfs_cache.cache('get_sched')
def get_sched():
    print('Fetching new schedule data')
    return gtfs_utils.static_from_file('google_transit.zip')

def get_realtime(trips, stop_id):
    rsched = gtfs_utils.realtime_from(realtime_url, auth=rtd_creds)
    return rsched.arrival_times(trips, stop_id)

sched = get_sched()

class Routes(Resource):
    def get(self):
        query = request.args.get('q')
        if query:
            return [r for r in sched.all_routes()
                    if query.lower() in r['route_short_name'].lower()]
        return sched.all_routes()

class Route(Resource):
    def get(self, route_id):
        if route_id not in sched.routes:
            abort(404, message='No route found with ID "{}"'.format(route_id))
        return sched.routes[route_id]

class Trips(Resource):
    def get(self, route_id):
        trips = sched.route_trips(route_id)
        query = request.args.get('q')
        if query:
            return [t for t in trips
                    if query.lower() in t['trip_headsign'].lower()]
        return trips

class Trip(Resource):
    def get(self, trip_id):
        if trip_id not in sched.trips:
            abort(404, message='No trip found with ID "{}"'.format(trip_id))
        return sched.trips[trip_id]

class Stops(Resource):
    def get(self, trip_id):
        if trip_id not in sched.trips:
            abort(404, message='No trip found with ID "{}"'.format(trip_id))
        stops = sched.trip_stops(trip_id)
        query = request.args.get('q')
        if query:
            return [r for r in stops
                    if query.lower() in r['stop_name'].lower()]
        return stops

class Stop(Resource):
    def get(self, stop_id):
        if stop_id not in sched.stops:
            abort(404, message='No stop found with ID "{}"'.format(stop_id))
        return sched.stops[stop_id]

class Realtime(Resource):
    def get(self):
        route_id = request.args.get('route')
        headsign = request.args.get('headsign')
        stop_id = request.args.get('stop')
        if not (route_id and headsign and stop_id):
            abort(400, message='Query params "route", "headsign", and "stop" are required')
        trips = sched.route_trips(route_id)
        trips = [t for t in trips if t['trip_headsign'] == headsign]
        if not trips:
            abort(404, message='No trips found with headsign "{}"'.format(headsign))
        if stop_id not in sched.stops:
            abort(404, message='No stop found with ID "{}"'.format(stop_id))
        return get_realtime(trips, stop_id)

app = Flask(__name__)
api = Api(app)

api.add_resource(Routes, '/routes')
api.add_resource(Route, '/routes/<route_id>')
api.add_resource(Trips, '/routes/<route_id>/trips')
api.add_resource(Trip, '/trips/<trip_id>')
api.add_resource(Stops, '/trips/<trip_id>/stops')
api.add_resource(Stop, '/stops/<stop_id>')
api.add_resource(Realtime, '/realtime')

if __name__ == '__main__':
    app.run(debug=True)
