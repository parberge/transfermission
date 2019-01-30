from transfermission.utils import age, read_config
from transfermission.config import config
from transfermission.rule import Rule
from transfermission.episode_manager import EpisodeManager
from datetime import datetime

import logging

log = logging.getLogger()
handler = logging.StreamHandler()
log.addHandler(handler)
# Might be useful to set log level in tests to debug
log.setLevel(logging.CRITICAL)


def test_age():
    test = age(datetime.now())
    assert isinstance(test, int)
    assert test == 0


def test_config():
    test = config
    assert isinstance(test, dict)
    assert test == {}
    test.update(read_config('config.yml.example'))
    assert test['transmission_url']

    # Not the most useful test, but it will test the __setitem__ of Config class
    test['foo'] = 'bar'
    assert test['foo'] == 'bar'

    # Verify that the dict is still empty
    assert test == {}


def test_rules():
    test = Rule()
    assert isinstance(test, Rule)
    assert test.id == 1

    # Create a fake class to get the expected attribute
    class FakeTorrent:
        name = 'fake torrent name'

    fake_torrent = FakeTorrent()
    assert test.run_condition(fake_torrent, 'name', 'fake') is True
    assert test.run_condition(fake_torrent, 'name', 'should not match') is False


def test_example_config():
    example_config = read_config('config.yml.example')
    assert isinstance(example_config, dict)

    # These are the options that should exist in the example config
    options = ('transmission_url', 'transmission_user', 'transmission_password', 'rules')
    for option in options:
        assert option in example_config

    assert isinstance(example_config['rules'], list)


def test_episode_manager(tmp_path):
    fake_shows_dir = tmp_path / "series"
    fake_shows_dir.mkdir()
    test = EpisodeManager()
    test.find_existing_shows(tv_shows_path=fake_shows_dir)

    # Our tmpdir doesn't contain any shows so existing shows should still be empty
    assert test.existing_shows == {}

    fake_show = fake_shows_dir / "the fake show" / "Season 1"
    fake_show.mkdir(parents=True)
    test.find_existing_shows(tv_shows_path=fake_shows_dir)

    existing_fake_show = test.existing_shows.get('fakeshow')
    assert isinstance(existing_fake_show, dict
                      )
    assert existing_fake_show
    for key in ('name', 'seasons'):
        assert key in existing_fake_show

    assert isinstance(existing_fake_show['seasons'], dict)
    assert existing_fake_show['seasons'][1]
