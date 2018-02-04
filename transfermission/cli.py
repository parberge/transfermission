#!/bin/env python
import logging
import re
import click
import transmissionrpc

from utils import read_config, age, remove_torrent, process_item

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
def cli(dry_run, log_level):
    log_levels = {
        'info': logging.INFO,
        'debug': logging.DEBUG,
    }
    log.setLevel(log_levels.get(log_level))
    if log_level == 'debug':
        # Set transmissonrpc logger to logging INFO when we run debug
        logging.getLogger('transmissionrpc').setLevel(logging.INFO)

    config = read_config('transfermission_config.yaml')
    movie_identifiers = config['movie_identifiers']
    user = config['transmission_user']
    password = config['transmission_password']
    host = config['transmission_host']
    port = config['transmission_port']

    if dry_run:
        log.info('Dry run mode. No changes will be done')

    transmission_session = transmissionrpc.Client(address=host, port=port, user=user, password=password)

    torrents = transmission_session.get_torrents()

    for torrent in torrents:
        operation = None
        log.debug('Checking torrent %s', torrent.name)
        log.debug('Status is: %s',  torrent.status)


        # Use regex to identify if movie or tv serie.
        # TODO: Use external resource (imdb etc) for this instead
        if re.search('s\d\de\d\d', torrent.name, re.I):
            file_type = 'series'

        elif re.search('\.s\d\d\.', torrent.name, re.I):
            log.info('Probably a whole season. Not supported...')
            continue

        elif True in (item.lower() in torrent.name for item in movie_identifiers):
            file_type = 'movie'

        else:
            log.warning('Unable to identify file type of file %s', torrent.name)
            log.debug('Current movie identifiers: %s' % movie_identifiers)

        log.debug('File type is: %s', file_type)
        file_seed_time = config.get('{0}_seed_time'.format(file_type))
        log.debug('File max seed time in days: %s', file_seed_time)

        torrent_age = 0
        if torrent.date_done:
            torrent_age = age(torrent.date_done)
            log.debug('Torrent been seeding for %s day(s)', torrent_age)

        if torrent_age > file_seed_time or torrent.isFinished:
            log.debug('Torrent %s is complete', torrent.name)
            operation = 'move'
        elif torrent.status != 'downloading':
            operation = 'symlink'

        else:
            log.warning('Torrent %s is not seeding or finished', torrent.name)

        if operation == 'move':
            result = remove_torrent(torrent, session=transmission_session, dry_run=dry_run)
            if not result:
                log.warning('Skipping moving torrent since stop failed')

        if operation:
            log.debug('Operation is: %s', operation)
            process_item(item_type=file_type, torrent=torrent,
                         operation=operation, config=config, dry_run=dry_run)
        else:
            log.error('No operation selected for torrent %s', torrent.name)


if __name__ == '__main__':
    cli()
