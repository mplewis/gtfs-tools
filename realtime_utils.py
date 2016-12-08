import gtfs_realtime_pb2

import requests
import pygtfs

from datetime import datetime

class StaticSched:
    def __init__(self, db):
        self.sched = pygtfs.Schedule(db)

    def trips_with_kw(self, kw):
        return [t for t in self.sched.trips if kw in t.trip_headsign]

class RealtimeSched:
    def __init__(self, sched):
        self.sched = sched

    def arrival_times(self, trips, stop_id):
        trip_ids = [t.trip_id for t in trips]
        vehicles = []
        for e in self.sched.entity:
            update = e.trip_update
            if update.trip.trip_id in trip_ids:
                vehicles.append(update.stop_time_update)
        arrivals = []
        for vehicle in vehicles:
            for stop in vehicle:
                if stop.stop_id == stop_id:
                    time = datetime.fromtimestamp(stop.arrival.time)
                    arrivals.append(time)
        return sorted(arrivals)

def realtime_from(url, **kwargs):
    resp = requests.get(url, **kwargs)
    resp.raise_for_status()
    raw = resp.content
    parsed = gtfs_realtime_pb2.FeedMessage()
    parsed.ParseFromString(raw)
    return RealtimeSched(parsed)
