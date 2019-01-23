from transfermission.utils import age
from transfermission.config import Config
from transfermission.rule import Rule
from datetime import datetime


def test_age():
    test = age(datetime.now())
    assert isinstance(test, int)
    assert test == 0


def test_config():
    test = Config()
    assert isinstance(test, dict)
    assert test == {}


def test_rules():
    test = Rule()
    assert isinstance(test, Rule)
    assert test.id == 1
