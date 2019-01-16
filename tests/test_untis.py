from transfermission.utils import age
from datetime import datetime


def test_age():
    test = age(datetime.now())
    assert isinstance(test, int)
    assert test == 0
