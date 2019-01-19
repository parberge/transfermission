import logging
import re
from datetime import datetime

from config import config

log = logging.getLogger(__name__)

class Rule:
    id = 0
    def __init__(self, conditions=None, actions=None):
        self.id = Rule.id = Rule.id + 1
        self.conditions = conditions or []
        self.actions = actions or []

    def matches(self, torrent):
        return all([
            self.run_condition(torrent, condition_name, condition_value)
            for condition_name, condition_value in self.conditions.items()
        ])

    def run_condition(self, torrent, condition_name, condition_value):
        return getattr(self, f'_condition_{condition_name}')(torrent, condition_value)

    def run_actions(self, torrent):
        for i, action in enumerate(self.actions, 1):
            # TODO: support complex config as arg
            action_name, action_arg = list(action.items())[0]
            if config['dryrun']:
                log.info('Dryrun - skipping running action #%s: %s', i, action_name)
            else:
                log.info('Running action #%s: %s', i, action_name)
                getattr(self, f'_action_{action_name}')(torrent, action_arg)

    def _condition_name(self, torrent, pattern):
        return re.search(pattern, torrent.name)

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


    def _action_move_data(self, torrent, path):
        log.info('Moving "%s" to %s', torrent.name, path)
        # Give a generous timeout since moving loads of GBs can take a while
        torrent.move_data(path, timeout=1200)

    def _action_call_url(self, torrent, url):
        log.info('Calling URL "%s"', url)
