# pregonero
Simple Python Mastodon bot.
## Requirements
Python3 setup including yaml and mastodon.py.

You can install them using:
```
$ pip3 install pyaml mastodon.py
```
## Config file
The YAML config file is required, as it must contain two mandatory parameters: `token` and `instance_uri`. 
The default expected name is `pregonero.yaml`, in the same path as the script, but any config file can 
be passed using the `--config` command line parameter.

The last (optional) parameter is `message`. If not speficied it defaults to 'There are {users} souls at {instance}'

Sample config file:
```
token: YOUR_USER_API_TOKEN_GOES_HERE
instance_uri: https://your.uri.goes.here/
message: 'There are {users} souls at {instance}'
```
## Running
The simplest way is:
```
$ ./pregonero.py
```

Passing a specific config file:
```
$ ./pregonero.py --config config_file
```

By default, the script does no toot anything, but prints out what would have been posted.
```
$ ./pregonero.py --config pregonero2.yaml 
Would have posted: "There are 23 souls at your.mastodon.site"
```

In order for the script to effectively post, the `--do` command line parameter must be used.
```
$ ./pregonero.py --do
$
```
