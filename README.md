# gtfs-tools

[![CircleCI](https://circleci.com/gh/mplewis/gtfs-tools.svg?style=svg)](https://circleci.com/gh/mplewis/gtfs-tools)

Some useful stuff for working with GTFS [Static](https://developers.google.com/transit/gtfs/) and [Realtime](https://developers.google.com/transit/gtfs-realtime/) data.

# Server

`server.py` is a Flask server that provides:

* route list/search
* list all trips in a route
* trip info/search
* list all stops in a trip
* stop info/search
* **realtime arrival estimates** for a route, headsign, and stop

# Running the Server

Create and fill out `config.py` with the static and realtime URLs and (optional) request args:

```python
class Base:
    DEBUG = False
    TESTING = False
    GTFS_STATIC = {
        'url': 'http://www.example.com/gtfs_static.zip',
        'args': {}
    }
    GTFS_REALTIME = {
        'url': 'http://www.example.com/gtfs_realtime.pb',
        'args': {'auth': ('keanu', '>50mph')}
    }

class Debug(Base):
    DEBUG = True
```

Then start the server:

```sh
pip install -r requirements.txt  # install dependencies
python server.py  # production
DEBUG=TRUE python server.py  # debug
```

# Testing

```sh
pip install -r test/requirements.txt
py.test
```

# License

MIT
