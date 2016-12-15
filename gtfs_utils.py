import gtfs_realtime_pb2

import requests

from csv import DictReader
from io import BytesIO
from tempfile import TemporaryDirectory
from zipfile import ZipFile
from os.path import join

class StaticSched:
    def __init__(self, gtfs_path):
        self.routes = {}
        with open(join(gtfs_path, 'routes.txt')) as f:
            self.routes = {r['route_id']: r for r in DictReader(f)}
        with open(join(gtfs_path, 'trips.txt')) as f:
            self.trips = {r['trip_id']: r for r in DictReader(f)}
        with open(join(gtfs_path, 'stops.txt')) as f:
            self.stops = {r['stop_id']: r for r in DictReader(f)}
        with open(join(gtfs_path, 'stop_times.txt')) as f:
            self.stop_times = list(DictReader(f))

    def all_routes(self):
        return list(self.routes.values())

    def route_trips(self, route_id):
        return [t for t in self.trips.values() if t['route_id'] == route_id]

    def trip_stops(self, trip_id):
        filtered = [st for st in self.stop_times if st['trip_id'] == trip_id]
        stop_ids = {st['stop_id'] for st in filtered}
        return [self.stops[i] for i in stop_ids]

class RealtimeSched:
    def __init__(self, sched):
        self.sched = sched

    def arrival_times(self, trips, stop_id):
        trip_ids = [t['trip_id'] for t in trips]
        vehicles = []
        for e in self.sched.entity:
            update = e.trip_update
            if update.trip.trip_id in trip_ids:
                vehicles.append(update.stop_time_update)
        arrivals = []
        for vehicle in vehicles:
            for stop in vehicle:
                if stop.stop_id == stop_id:
                    arrivals.append(stop.arrival.time)
        return sorted(arrivals)

def _static_from(fileobj):
    zf = ZipFile(fileobj)
    with TemporaryDirectory() as td:
        zf.extractall(path=td)
        return StaticSched(td)

def static_from_url(url, **kwargs):
    resp = requests.get(url, **kwargs)
    resp.raise_for_status()
    return _static_from(BytesIO(resp.content))

def static_from_file(path):
    with open(path, 'rb') as f:
        return _static_from(f)

def realtime_from_url(url, **kwargs):
    resp = requests.get(url, **kwargs)
    resp.raise_for_status()
    raw = resp.content
    parsed = gtfs_realtime_pb2.FeedMessage()
    parsed.ParseFromString(raw)
    return RealtimeSched(parsed)
