import datetime
import os
import re
import shutil
from time import sleep
import yaml
import logging


log = logging.getLogger(__name__)

def read_config(file_path):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    config_file = "{0}/{1}".format(dir_path, file_path)
    with open(config_file) as f:
        config = yaml.load(f)

    return config


def age(date):
    """
    Return the number of days between now and date.
    Date needs to be a datetime object.
    """
    time_difference = datetime.datetime.now() - date
    return time_difference.days


def remove_torrent(torrent, session, dry_run=False):
    """
    Stops and removes torrent from transmission
    """
    if dry_run:
        log.info('Would stop and remove torrent %s', torrent.name)
    else:
        if torrent.status != 'stopped':
            log.info('Stopping torrent %s', torrent.name)
            session.stop_torrent(torrent.id)
            for _ in range(5):
                torrent_session = session.get_torrent(torrent.id)
                log.debug(
                    'torrent status is: %s', torrent_session.status
                )
                if torrent_session.status == 'stopped':
                    break

                sleep(3)

            else:
                log.warning('Failed to stop torrent %s', torrent.name)
                return False

        log.info('Removing torrent %s', torrent.name)
        session.remove_torrent(torrent.id)
        return True


def move(file_src_path, file_dest_path, dry_run=False):
    """ Move a file """
    if dry_run:
        log.info('Would move %s to %s' % (file_src_path.rstrip('/'), file_dest_path))
    else:
        log.info('Moving %s to %s' % (file_src_path.rstrip('/'), file_dest_path))
        if os.path.islink(file_dest_path):
            log.debug('destination is a link, removing it')
            os.remove(file_dest_path)

        shutil.move(file_src_path.rstrip('/'), file_dest_path)


def handle_file(file_src_path, file_dest_path, operation, dry_run=False):
    """ Symlink or move files """

    log.debug('Dest is: %s', file_dest_path)
    if operation == 'symlink':
        if not os.path.islink(file_dest_path):
            if dry_run:
                log.info("Would've Symlinked: %s to %s" % (file_dest_path, file_src_path))
            else:
                os.symlink(file_src_path, file_dest_path)
                log.info('Created link: %s to %s' % (file_dest_path, file_src_path))
        else:
            if os.path.exists(file_dest_path):
                log.debug('Symlink already exists')
            else:
                log.warning("Symlink %s might be broken", file_dest_path)

    elif operation == 'move':
        move(file_src_path, file_dest_path, dry_run=dry_run)
    else:
        raise ValueError('Operation not supported')


def process_item(item_type, torrent, config, operation, dry_run=False):
    """ Process file and do various actions """

    file_source = '{0}/{1}/'.format(
        config.get('download_dir'),
        torrent.name,
    )

    log.debug('File source path: %s', file_source)
    file_target = None

    if item_type == 'movie':
        file_target = '{0}/{1}'.format(
            config.get('movie_dir'),
            torrent.name,
        )

    elif item_type == 'series':

        season_regex = config.get('season_regex')
        if not season_regex:
            # I save my Season names as "Season 1", therefor exclude any starting zeros in season
            season_regex = 's0?(\d+)e\d\d'
        season = re.search(season_regex, torrent.name, re.I).group(1)
        log.debug('Season: %s', season)

        tv_show = None
        for serie in os.listdir(config.get('series_dir')):
            if serie.replace(" ", ".").lower() in torrent.name.lower():
                tv_show = serie
                break

        if not tv_show:
            log.warning('No matching tv show in %s for torrent %s' % (config.get('series_dir'), torrent.name))
            return

        if not season:
            log.info('Unable to identify season')
            return
        else:
            season_path = '{0}/{1}/Season {2}'.format(
                config.get('series_dir'),
                tv_show,
                season,
            )

        if not os.path.isdir(season_path):
            if not dry_run:
                log.info('Missing season directory, creating it')
                os.mkdir(season_path)
            else:
                log.info('Would create missing season dir: %s', season_path)

        file_target = '{0}/{1}'.format(
            season_path,
            torrent.name,
        )
        log.debug('File destination: %s', file_target)

    else:
        log.debug("Item type '%s' unhandled", item_type)

    handle_file(file_source, file_target, operation, dry_run)
