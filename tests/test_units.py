from transfermission.utils import age, read_config
from transfermission.config import config
from transfermission.rule import Rule
from datetime import datetime


def test_age():
    test = age(datetime.now())
    assert isinstance(test, int)
    assert test == 0


def test_config():
    test = config
    assert isinstance(test, dict)
    assert test == {}


def test_rules():
    test = Rule()
    assert isinstance(test, Rule)
    assert test.id == 1


def test_read_config():
    test_config = read_config('config.yml.example')
    assert isinstance(test_config, dict)

    # These are the options that should exist in the example config
    options = ('transmission_url', 'transmission_user', 'transmission_password', 'rules')
    for option in options:
        assert option in test_config

    assert isinstance(test_config['rules'], list)
