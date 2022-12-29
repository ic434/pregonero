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
# - message
#   the message can use thesee placeholders, instance, users, statuses, date - datetime object ) :
#   - instance - instance name
#   - users - number of users
#   - statuses - number of tooted statuses
#   - date - a datetimeobject of current date and time, can also use properties: date.year, date.month, date.day, etc

eye = ' 👁️'

localpath = os.path.dirname(sys.argv[0])
default_config_file = os.path.join(localpath, 'pregonero.yaml')
status_file = os.path.join(localpath, '.pregonero.yaml')

parser = argparse.ArgumentParser(description="Toot user count usign given (bot) account.", fromfile_prefix_chars='@')
parser.add_argument('--config', help='YAML config file to use (accepted variables: token, instance_uri, message)', default=None)
parser.add_argument('--date', help='yyyy-mm-dd date for testing different run dates', default=None)
parser.add_argument('--users', help='Number of users, for testing', type=int, default=None)
parser.add_argument('--hit', help='Goal hit, for testing', type=int, default=None)
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
    'developer_plus': "Us, developers, celebrate exceeding {users} souls at {instance}",
    'milestones': [50, 60, 81, 100, 121, 144, 169]
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

today = datetime.datetime.now()
if args.date is not None:
    try:
        today = datetime.datetime.strptime(args.date, "%Y-%m-%d")
    except Exception as e:
        print("Ignoring {} non-parseable date (yyyy-mm-dd)".format(args.date,))
        pass

mastodon = Mastodon(
    access_token=config['token'],
    api_base_url=config['instance_uri']
)

# Get data from the server
instance_data = mastodon.instance()
users = instance_data["stats"]["user_count"] if args.users is None else args.users
instance = instance_data["uri"]
statuses = instance_data["stats"]["status_count"]
reportedusers = users
day_signature = 'message_' + str(today.month) + '_' + str(today.day)
last_power_of_two = int(math.pow(2, int(math.log(users, 2))))
if args.hit is not None:
    status['hit'] = args.hit

message = config['message']
if day_signature in config:
    message = config[day_signature]
elif users <= 256 and last_power_of_two > status['hit'] and last_power_of_two > status['users']:
    status['hit'] = last_power_of_two
    message = config['developer'] if users == last_power_of_two else config['developer_plus']
    reportedusers = last_power_of_two
elif 'milestones' in config:
    for goal in config['milestones']:
        if users >= goal and goal > status['hit'] and goal > status['users']:
            status['hit'] = goal
            message = config['wow'] if users == goal else config['wow_plus']
            reportedusers = goal

status['users'] = users

toot = message.format(instance = instance, users = reportedusers, statuses = statuses, date = today)
toot = toot + eye

# Finish
if dryrun:
    print('Would have posted: "{}"'.format(toot))
else:
    mastodon.status_post(toot)

if not dryrun:
    with open(status_file, 'w') as f:
        yaml.dump(status, f)
else:
    print("Would store hit: {} users: {}".format(status['hit'], status['users']))