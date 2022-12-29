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

TO EXPAND
wow
wow_plus
developer
developer_plus
milestones

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

An additional parameter can be fed to the script:

```
$ ./pregonero.py --date 2022-12-29
$
```

It sets the _current_ date for the script, to test different running dates.

Running the script also generates a status file, `.pregonero.yaml`, for internal use. The file is generated in the same folder of the script on its first non-dry-run run, and should not be deleted or modified manually. Deleting it would only affect the next run of the script.
