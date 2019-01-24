import os
import re
import logging

log = logging.getLogger(__name__)


class EpisodeManager:
    # Cache existing shows on class
    existing_shows = {}

    @classmethod
    def get_episode_path(cls, episode_name, tv_shows_path, season_template):
        # Populate class stored cache of existing shows
        if not cls.existing_shows:
            cls.find_existing_shows(tv_shows_path)
        # Guess some metadata from episode name
        episode_info = cls.get_episode_info(episode_name)
        if not episode_info:
            # Couldn't derive episode data from name
            return
        # Try to get a matching tv show
        show_info = cls.existing_shows.get(episode_info['show_slug'], None)
        if not show_info:
            # No matching show directory found
            return
        # Add season to show info if its missing
        if not episode_info['season'] in show_info['seasons']:
            show_info['seasons'][episode_info['season']] = season_template.format(episode_info['season'])
        # Build a path to where the episode should go
        target_season_path = os.path.join(
            tv_shows_path,
            show_info['name'],
            show_info['seasons'][episode_info['season']]
        )
        return target_season_path

    @classmethod
    def find_existing_shows(cls, tv_shows_path):
        """
        Build a dict with information about shows:
        {
            show_slug: {
                'name': show name,
                'seasons': {
                    int(season number): directory name
                }
            }
        }
        """
        shows = {}
        # Map {slugified name: show name}
        for show in os.listdir(tv_shows_path):
            show_path = os.path.join(tv_shows_path, show)
            if not os.path.isdir(show_path):
                continue
            show_slug = re.sub('\W', '', show.lower().replace('the', ''))
            shows[show_slug] = {'name': show}

            # Add seasons info as a map of {int(season number): directory name}
            seasons = {}
            season_dirs = os.listdir(show_path)
            for season_dir in season_dirs:
                if not os.path.isdir(os.path.join(show_path, season_dir)):
                    continue
                match = re.search('\d+', season_dir)
                if match:
                    # Dicts with int as key are weird but handy
                    seasons[int(match.group(0))] = season_dir
            shows[show_slug]['seasons'] = seasons
        cls.existing_shows = shows

    @staticmethod
    def get_episode_info(name):
        matches = re.findall( '^(.*?)se?(\d\d?)ep?\d\d?', name.lower())
        if not matches:
            return False

        show_name = matches[0][0]
        season = matches[0][1]
        # remove non alphanumerics and 'the's for matching with existing dirs
        show_slug = re.sub('\W', '', show_name.replace('the', ''))
        return {'show_name': show_name, 'show_slug': show_slug, 'season': int(season)}
