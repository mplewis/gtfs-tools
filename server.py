import gtfs_utils

from flask import Flask, request
from flask_restful import Resource, Api, abort
from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options

app = Flask(__name__)
api = Api(app)

cache = CacheManager(**parse_cache_config_options({
    'cache.type': 'file',
    'cache.data_dir': '/tmp/gtfs-tools/data',
    'cache.lock_dir': '/tmp/gtfs-tools/lock',
}))

@cache.cache('get_sched')
def get_sched():
    print('Fetching new schedule data')
    return gtfs_utils.static_from_file('google_transit.zip')

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
    def get(self):
        route_id = request.args.get('route')
        if not route_id:
            abort(400, message='Provide a route ID: /trips?route=ROUTE_ID')
        trips = sched.route_trips(route_id)
        headsign = request.args.get('headsign')
        if headsign:
            return [t for t in trips
                    if headsign.lower() in t['trip_headsign'].lower()]
        return trips

api.add_resource(Routes, '/routes')
api.add_resource(Route, '/routes/<route_id>')
api.add_resource(Trips, '/trips')

if __name__ == '__main__':
    app.run(debug=True)
