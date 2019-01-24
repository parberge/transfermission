#!/usr/bin/env python
import logging
import re
from datetime import datetime, timedelta

import click
import transmissionrpc

from transfermission.config import config
from transfermission.rule import Rule
from transfermission.utils import read_config

log = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter(
        '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
log.addHandler(handler)


@click.command()
@click.option('--config-file', '-f', help='Path to config file. Defaults to ./config.yml', default='config.yml')
@click.option('--dry-run', '-d', help='Don\'t run actions', is_flag=True)
@click.option('--verbose', '-v', help='Verbose', is_flag=True)
@click.option('--name-condition', '-n', help='Add an extra name condition to all rules. '
    'Handy for temporarily limiting the scope.',
)
def cli(config_file, dry_run, verbose, name_condition=None):
    log.setLevel(logging.DEBUG if verbose else logging.INFO)
    if verbose:
        # Set transmissonrpc logger to logging INFO when we run debug
        logging.getLogger('transmissionrpc').setLevel(logging.INFO)

    config.update(read_config(config_file))
    config['dryrun'] = dry_run
    if dry_run:
        log.info('Dry run mode. No changes will be done')

    rules = [Rule(**rule_config) for rule_config in config['rules']]
    # A bit hacky perhaps, but convenient..
    if name_condition:
        [r.conditions.append({'name': name_condition}) for r in rules]

    transmission_session = transmissionrpc.Client(
        address=config['transmission_url'],
        user=config['transmission_user'],
        password=config['transmission_password']
    )
    torrents = transmission_session.get_torrents()

    #session = lambda: None
    #session.get_torrents = mock_torrents
    #torrents = session.get_torrents()
    for torrent in torrents:
        log.debug('Checking %s (%s)', torrent.name, torrent.status)
        for rule in rules:
            log.debug('Checking rule #%s conditions', rule.id)
            if rule.matches(torrent):
                log.info('%s matches rule #%s. Running actions.', torrent.name, rule.id)
                rule.run_actions(torrent)
                if rule.last:
                    break


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
    cli()