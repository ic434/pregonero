#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

from mastodon import Mastodon
import yaml
import argparse
import sys
import os

# Config file arguments
# - token
# - instance_uri
# - message (can use two placeholders, instance, users, statuses) 

default_message = 'There are {users} souls at {instance}'

localpath = os.path.dirname(sys.argv[0])
default_config_file = os.path.join(localpath, 'pregonero.yaml')

parser = argparse.ArgumentParser(description="Toot user count usign given (bot) account.", fromfile_prefix_chars='@')
parser.add_argument('--config', help='YAML config file to use (accepted variables: token, instance_uri, message)', default=None)
groupd = parser.add_mutually_exclusive_group()
groupd.add_argument("--dry-run", help="Do not post, just test", action="store_true", default=True)
groupd.add_argument("--do", help="Post", action="store_true", default=False)
args = parser.parse_args()

dryrun = True
if args.do:
    dryrun = False

# Configure
config = {}
try:
    with open(args.config if args.config is not None else default_config_file) as f:
        config = yaml.safe_load(f)
except Exception as e:
    print("Config file error: {}".format(e))

if 'instance_uri' not in config or config['instance_uri'] is None:
    raise Exception('Instance_uri is mandatory')

if 'token' not in config or config['token'] is None:
    raise Exception('Token is mandatory')

if 'message' not in config:
    config['message'] = default_message

mastodon = Mastodon(
    access_token=config['token'],
    api_base_url=config['instance_uri']
)

# Get data from the server
instance = mastodon.instance()
toot = config['message'].format(instance = instance["uri"], users = instance["stats"]["user_count"], statuses = instance["stats"]["status_count"])

# Finish
if dryrun:
    print('Would have posted: "{}"'.format(toot))
else:
    mastodon.status_post(toot)
