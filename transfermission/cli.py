#!/usr/bin/env python
import logging
import re
import click
import transmissionrpc
from datetime import datetime, timedelta

from utils import read_config, age, remove_torrent, process_item
from rule import Rule

log = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter(
        '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
log.addHandler(handler)


@click.command()
@click.option(
    '--dry-run',
    help='Show what would be done',
    is_flag=True,
)
@click.option(
    '--log-level',
    help='Log level',
    default='info',
)
def cli2(dry_run, log_level):
    log_levels = {
        'info': logging.INFO,
        'debug': logging.DEBUG,
    }
    log.setLevel(log_levels.get(log_level))
    if log_level == 'debug':
        # Set transmissonrpc logger to logging INFO when we run debug
        logging.getLogger('transmissionrpc').setLevel(logging.INFO)

    log.debug('Reading config')
    config = read_config('transfermission_config.yaml')
    user = config['transmission_user']
    password = config['transmission_password']
    url = config['transmission_url']
    rules = [Rule(**rule_config) for rule_config in config['rules']]

    if dry_run:
        log.info('Dry run mode. No changes will be done')

    #transmission_session = transmissionrpc.Client(address=url, user=user, password=password)

    #torrents = transmission_session.get_torrents()
    torrents = mock_torrents()

    for torrent in torrents:
        log.debug('Checking torrent %s', torrent.name)
        log.debug('Status is: %s',  torrent.status)
        for rule in rules:
            if rule.matches(torrent):
                log.info('Torrent %s matches rule #%s. Running actions.', torrent.name, rule.id)
                rule.run_actions(torrent)


def mock_torrents():
    torrents = []
    for i in range(3):
        t = lambda: None
        t.id = i+1
        t.name = f'torrent {t.id}'
        t.status = 'seeding'
        t.date_done = datetime.now() - timedelta(days=2)
        t.ratio = 4

        torrents.append(t)
    return torrents


if __name__ == '__main__':
    cli2()
