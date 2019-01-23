from transfermission.utils import age
from transfermission.config import config
from datetime import datetime


def test_age():
    test = age(datetime.now())
    assert isinstance(test, int)
    assert test == 0


def test_config():
    test = config
    assert isinstance(test, dict)
    assert test == {}
