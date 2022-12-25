#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

from mastodon import Mastodon
import yaml
import argparse
import datetime
import math
import sys
import os

# Config file arguments
# - token
# - instance_uri
# - message (can use three placeholders, instance, users, statuses) 

eye = ' 👁️'

milestones = (50, 60, 81, 100, 121, 144, 169)

localpath = os.path.dirname(sys.argv[0])
default_config_file = os.path.join(localpath, 'pregonero.yaml')
status_file = os.path.join(localpath, '.pregonero.yaml')

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
config = {
    'message': 'There are {users} souls at {instance}',
    'wow': "Let's celebrate that we have reached {users} souls at {instance}",
    'wow_plus': "Let's celebrate that we have exceeded {users} souls at {instance}",
    'developer': "Us, developers, celebrate reaching {users} souls at {instance}",
    'developer_plus': "Us, developers, celebrate exceeding {users} souls at {instance}"
}
try:
    with open(args.config if args.config is not None else default_config_file) as f:
        config.update(yaml.safe_load(f))
except Exception as e:
    print("Config file error: {}".format(e))

status = {'users': 0, 'hit': 0}
try:
    with open(status_file) as f:
        status.update(yaml.safe_load(f))
except Exception as e:
    pass

if 'instance_uri' not in config or config['instance_uri'] is None:
    raise Exception('Instance_uri is mandatory')

if 'token' not in config or config['token'] is None:
    raise Exception('Token is mandatory')

mastodon = Mastodon(
    access_token=config['token'],
    api_base_url=config['instance_uri']
)

# Get data from the server
instance_data = mastodon.instance()
users = instance_data["stats"]["user_count"]
instance = instance_data["uri"]
statuses = instance_data["stats"]["status_count"]
reportedusers = users
today = datetime.datetime.now()
day_signature = 'message_' + str(today.month) + '_' + str(today.day)
last_power_of_two = int(math.pow(2, int(math.log(users, 2))))

message = config['message']
if day_signature in config:
    message = config[day_signature]
elif users <= 256 and last_power_of_two > status['users']:
    status['hit'] = last_power_of_two
    message = config['developer'] if users == last_power_of_two else config['developer_plus']
    reportedusers = last_power_of_two
else:
    for goal in milestones:
        if goal > status['users'] and users >= goal:
            status['hit'] = goal
            message = config['wow'] if users == goal else config['wow_plus']
            reportedusers = goal
            break

status['users'] = users

toot = message.format(instance = instance, users = users, statuses = statuses)
toot = toot + eye

# Finish
if dryrun:
    print('Would have posted: "{}"'.format(toot))
else:
    mastodon.status_post(toot)

if not dryrun:
    with open(status_file, 'w') as f:
        yaml.dump(status, f)