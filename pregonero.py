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
# TODO: update config file arguments
# - token
# - instance_uri
# - message
#   the message can use thesee placeholders, instance, users, statuses, date - datetime object ) :
#   - instance - instance name
#   - users - number of users
#   - statuses - number of tooted statuses
#   - date - a datetimeobject of current date and time, can also use properties: date.year, date.month, date.day, etc

def format_message(msg, instance, users, statuses, date):
    if isinstance(msg, str):
        try:
            return msg.format(instance=instance, users=users, statuses=statuses, date=date)
        except Exception as e:
            print('Error formatting message {}: {}'.format(msg, e))
    return None

eye = ' 👁️'

localpath = os.path.dirname(sys.argv[0])
# TODO: think of removing config & status file from binary folder and move them to somewhere else
default_config_file = os.path.join(localpath, 'pregonero.yaml')
status_file = os.path.join(localpath, '.pregonero.yaml')

parser = argparse.ArgumentParser(description="Toot user count usign given (bot) account.", fromfile_prefix_chars='@')
# TODO: Update README.md to reflect all the options
parser.add_argument('--config', help='YAML config file to use (accepted variables: token, instance_uri, message)', default=None)
parser.add_argument('--date', help='yyyy-mm-dd date for testing different run dates', default=None)
parser.add_argument('--users', help='Number of users, for testing', type=int, default=None)
parser.add_argument('--lastusers', help='Number of stored users, for testing', type=int, default=None)
parser.add_argument('--statuses', help='Statuses, for testing', type=int, default=None)
parser.add_argument('--laststatuses', help='Number of stored statuses, for testing', type=int, default=None)
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
    'statuses': 'Hey, look! We have reached {statuses} statuses at {instance}',
    'statuses_plus': 'Hey, look! We have exceeded {statuses} statuses at {instance}',
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

status = {'users': 0, 'statuses': 0}
modulus = 100 if 'modulus' not in config else config['modulus']

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
day_signature = ('message_' + str(today.month) + '_' + str(today.day), 'message_' + str(today.day))

if args.date is not None:
    try:
        today = datetime.datetime.strptime(args.date, "%Y-%m-%d")
        day_signature = ('message_' + str(today.month) + '_' + str(today.day), 'message_' + str(today.day))
        print("Using {} as today with signature {}".format(today, day_signature))
    except Exception as e:
        print("Ignoring {} non-parseable date (yyyy-mm-dd): {}".format(args.date, e))

mastodon = Mastodon(
    access_token=config['token'],
    api_base_url=config['instance_uri']
)

# Get data from the server
instance_data = mastodon.instance()
users = instance_data["stats"]["user_count"] if args.users is None else args.users
instance = instance_data["uri"]
statuses = instance_data["stats"]["status_count"] if args.statuses is None else args.statuses
reportedusers = users
reportedstatuses = statuses
last_power_of_two = int(math.pow(2, int(math.log(users, 2))))
last_status_moduled = int(statuses / modulus) * modulus

# Debugging
if args.lastusers is not None:
    status['users'] = args.lastusers
if args.laststatuses is not None:
    status['statuses'] = args.laststatuses

messages = []

users_reported = False

# Check motds
date_hits = set(day_signature).intersection(config.keys())
if len(date_hits) > 0:
    for key in date_hits:
        messages.append(format_message(config[key], instance, users, statuses, today))

# Check programmer milestones
if users <= 65536 and last_power_of_two > status['users']:
    users_reported = users == last_power_of_two 
    messages.append(format_message(config['developer'] if users == last_power_of_two else config['developer_plus'], instance, last_power_of_two, statuses, today))

# By design, the generic milestones are only checked if they are higher than programmer milestones
if 'milestones' in config:
    for goal in reversed(sorted(config['milestones'])):
        if users >= goal and goal > last_power_of_two and goal > status['users']:
            users_reported = users_reported or users == goal
            messages.append(format_message(config['wow'] if users == goal else config['wow_plus'], instance, goal, statuses, today))
            break

# Has user number changed?
if not users_reported and users > status['users']:
    messages.append(format_message(config['users'], instance, users, statuses, today))
else:
    print('Same user count ({})'.format(status['users']))

# Check statuses milestones
if last_status_moduled >= status['statuses']:
    messages.append(format_message(config['statuses'] if statuses == last_status_moduled else config['statuses_plus'], instance, users, last_status_moduled, today))

# Store new status
status['users'] = users
status['statuses'] = statuses

messages = list(filter(lambda x: x is not None, messages))

# Finish
if len(messages) > 0:
    try:
        messages = [format_message(config['message'], instance, users, statuses, today)] + messages
        toot = '. '.join(messages)
        toot = toot + '.' + eye
        if dryrun:
            print('Would have posted: "{}"'.format(toot))
        else:
            mastodon.status_post(toot)
    except Exception as e:
        print('An exception occurred: {}'.format(e))
else:
    print('Nothing to say')

# Persist status
if not dryrun:
    with open(status_file, 'w') as f:
        yaml.dump(status, f)
else:
    print("Would store: {}".format(status,))