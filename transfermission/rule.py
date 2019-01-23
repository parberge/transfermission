import logging
import os
import re
from datetime import datetime

from transfermission.config import config

log = logging.getLogger(__name__)


class Rule:
    id = 0

    def __init__(self, conditions=None, actions=None):
        self.id = Rule.id = Rule.id + 1
        self.conditions = conditions or []
        self.actions = actions or []

    def matches(self, torrent):
        return all([
            # Each condition is a one key dict. Send in key and value as args.
            self.run_condition(torrent, *list(condition.items())[0])
            for condition in self.conditions
        ])

    def run_condition(self, torrent, condition_name, condition_value):
        res = getattr(self, f'_condition_{condition_name}')(torrent, condition_value)
        log.debug('Condition: %s: %s - %s', condition_name, condition_value, res)
        return res

    def run_actions(self, torrent):
        for i, action in enumerate(self.actions, 1):
            # TODO: support complex config as arg
            action_name, action_arg = list(action.items())[0]
            if config['dryrun']:
                log.info('Dryrun - skipping running action #%s: %s', i, action_name)
            else:
                log.info('Running action #%s: %s', i, action_name)
                action_method = getattr(self, f'_action_{action_name}')
                # Support simple or complex action config
                if isinstance(action_arg, dict):
                    action_method(torrent, **action_arg)
                else:
                    action_method(torrent, action_arg)

    def _condition_name(self, torrent, pattern):
        return bool(re.search(pattern, torrent.name))

    def _condition_name_not(self, *args, **kwargs):
        return not self._condition_name(*args, **kwargs)

    def _condition_completed(self, torrent, completed):
        return bool(torrent.date_done) == completed

    def _condition_ratio(self, torrent, ratio):
        return torrent.ratio >= ratio

    def _condition_age(self, torrent, days):
        return (datetime.now() - torrent.date_done).days >= days

    def _condition_size(self, torrent, size):
        """True if torrent total size is larger than `size` in MB"""
        # Bytes -> MBytes
        return torrent.totalSize/1024/1024 >= size

    def _condition_download_dir(self, torrent, path):
        return torrent.downloadDir == path

    def _action_move_data(self, torrent, path, use_dir=False):
        # Check if the first file is in a directory
        torrent_uses_dir = '/' in torrent.files()[0]['name']
        if use_dir and not torrent_uses_dir:
            dir_name = os.path.splitext(torrent.name)[0]
            path = os.path.join(path, dir_name)
            log.info('Adding directory to path: %s', path)

        log.info('Moving "%s" to %s', torrent.name, path)
        # Give a generous timeout since moving loads of GBs can take a while
        torrent.move_data(path, timeout=1200)

    def _action_call_url(self, torrent, url):
        log.info('Calling URL "%s"', url)
