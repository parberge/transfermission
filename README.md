# transfermission

## Intro
Python scripts for handling torrents in transmission (https://transmissionbt.com/).  
Having transmission with RPC enabled is required.

Features:
* automatically symlink movies and tv series while seeding.
* stop and remove torrents when seeded completed.
* move movie or tv show to your specified directory.


## Install
1. clone repository
2. Install depedencies
### With pipenv (recommended)
`pipenv shell && pipenv sync --dev`  
__Note__: Remove `--dev` if you don't want to install dev deps

#### With pip
`pip install -r requirements.txt`

## Configure
1. copy `transfermission_config.yaml.example` to `transfermission_config.yaml` (Keep it in the same dir)
2. Update `transfermission_config.yaml` to match your environment

## Running
Use `cli.py --help` to see available options.

### Examples
#### Dry run
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
