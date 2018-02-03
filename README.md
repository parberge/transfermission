# transfermission

## Intro
A script for handling torrents in transmission (https://transmissionbt.com/).  
Having transmission already setup is required.

Features:
* automatically symlink movies and tv series while seeding.
* stop and remove torrents when seeded completed.
* move movie or tv show to your specified directory.

## Install & configure
1. clone repository
2. pip install -r requirements.txt (recommend virtualenv ofc)
3. copy `transfermission_config.yaml.example` to `transfermission_config.yaml` (Keep it in the same dir)
4. Update `transfermission_config.yaml` to match your environment

## Running
Use `cli.py --help` to see available options.

### Examples
```
$ transfermission/cli.py --dry-run --log-level debug
2018-02-03 12:26:57,216 root         INFO     Dry run mode. No changes will be done
2018-02-03 12:26:57,237 root         DEBUG    Checking torrent My.Awesome.Movie.1080p.BluRay.x264
2018-02-03 12:26:57,237 root         DEBUG    Status is: seeding
2018-02-03 12:26:57,237 root         DEBUG    File type is: movie
2018-02-03 12:26:57,237 root         DEBUG    File max seed time in days: 10
2018-02-03 12:26:57,238 root         DEBUG    Torrent been seeding for 6 day(s)
2018-02-03 12:26:57,238 root         DEBUG    Operation is: symlink
2018-02-03 12:26:57,238 utils        DEBUG    File source path: /my/torrents/My.Awesome.Movie.1080p.BluRay.x264
2018-02-03 12:26:57,238 utils        DEBUG    Symlink already exists
