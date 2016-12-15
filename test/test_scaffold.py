import os

def test_env():
    assert os.environ.get('TESTING') == 'TRUE'
