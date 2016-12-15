from server import app as app_under_test

import sure  # noqa
from webtest import TestApp


app = TestApp(app_under_test)


def test_root():
    app.get('/', status=204)
