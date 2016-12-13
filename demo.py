import gtfs_utils

from pprint import pprint

print('Parsing schedule...')
sched = gtfs_utils.static_from_file('google_transit.zip')
print('Schedule ready.')

if __name__ == '__main__':
    # pprint([t for t in sched.route_trips('10') if 'Elitch' in t['trip_headsign']])
    pprint(sched.trip_stops('110478254'))
