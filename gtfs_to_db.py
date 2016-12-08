import requests
import pygtfs
import argparse
from tempfile import NamedTemporaryFile

def fetch_parse_gtfs(gtfs_zip_url, dest_db):
    resp = requests.get(gtfs_zip_url)
    resp.raise_for_status()
    with NamedTemporaryFile(prefix='gtfs-', suffix='.zip') as f:
        f.write(resp.content)
        parse_gtfs(f.name, dest_db)

def parse_gtfs(zip_path, dest_db):
    sched = pygtfs.Schedule(dest_db)
    pygtfs.append_feed(sched, zip_path)

def parse_args():
    p = argparse.ArgumentParser(
        description='Process GTFS data and store it into a database.')
    p.add_argument('gtfs_zip_url',
        help='The URL to a .zip of GTFS data.')
    p.add_argument('dest_db',
        help=('The DB to parse the data into. Either the name of a file '
              '(e.g. transit_data.sqlite) or a SQLAlchemy connection URL.'))
    return p.parse_args()

def main():
    args = parse_args()
    fetch_parse_gtfs(args.gtfs_zip_url, args.dest_db)

if __name__ == '__main__':
    main()
