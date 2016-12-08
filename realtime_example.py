from realtime_utils import StaticSched, realtime_from
from config import rtd_creds
from sqlalchemy.exc import SAWarning

import warnings
from datetime import datetime, timedelta

following = (
    # nickname, trip keyword, stop id
    ('Uptown to NE Denver', 'Central Park', '16660'),
    ('Cap Hill to Aurora', 'Billings', '12953'),
)

trip_update_url = 'http://www.rtd-denver.com/google_sync/TripUpdate.pb'

def check_arrival_times():
    static = StaticSched('denver_rtd.sqlite')
    realtime = realtime_from(trip_update_url, auth=rtd_creds)
    for name, kw, stop_id in following:
        trips = static.trips_with_kw(kw)
        arrivals = realtime.arrival_times(trips, stop_id)
        now = datetime.now()
        zero = timedelta(seconds=0)
        arrivals = [a for a in arrivals if a - now > zero]
        print(name)
        for arr_time in arrivals:
            print('    {}'.format(arr_time - now))

def main():
    with warnings.catch_warnings():
        # ignore SQLAlchemy warnings; they're caused by pygtfs
        warnings.simplefilter('ignore', category=SAWarning)
        check_arrival_times()

if __name__ == '__main__':
    main()
