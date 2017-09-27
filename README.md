# firechannel

An almost-dropin replacement for the GAE channels API using Firebase.

## Usage

### Setup

1. `pip install firechannel`
1. Include the firebase web [init snippet][setup] in your app
1. Include `static/firechannel.js` in your app

### On the frontend

Given an implementation like

``` javascript
var channel = new goog.appengine.Channel("{{token}}");
var socket = channel.open();

socket.onmessage = function(data) { console.log(data); };
```

change the first line to

``` javascript
var channel = new Firechannel("{{token}}");
```


### On the backend

Change your imports from

``` python
from google.appengine.api.channel import create_channel, send_message
```

to

``` python
from firechannel import create_channel, send_message
```


### Inside Firebase

Add the following rule using your [Firebase console][rules]:

``` json
{
  "rules": {
    ".read": false,
    ".write": false,
    "firechannels": {
      "$channelId": {
        ".read": "auth.uid == $channelId",
        ".write": false
      }
    }
  }
}
```

And that's about it.


## Cleaning up old channels

You can call `delete_channel` after you're done sending messages on
it.  This will remove it from Firebase immediately.

If that's not feasible, you can set up an hourly (or daily) cron job
and delete all channels that have last received a message some amount
of time ago like this:

``` python
from firechannel import find_all_expired_channels, delete_channel

# All channels that have last received a message over a day ago
expired_channels = find_all_expired_channels(max_age=86400)
for channel_id in expired_channels:
  delete_channel(channel_id)
```


## Testing

To run the tests, create a service account and point an env var called
`SERVICE_KEY_FILE_PATH` to it and another one called `FIREBASE_PROJECT`
to the name of your project.  Finally, run `py.test`.

### GAE tests

To run the AppEngine tests, point an env var called `APPENGINE_SDK_PATH`
to the base path of your GAE SDK and run `py.test tests_appengine`.


## Authors

`firechannel` was authored at [Leadpages][leadpages].  You can find
out more about contributors [here][contributors].  We welcome
contributions, and [we're always looking][careers] for more
engineering talent!


## Contributing

Please read [our contributor's guide](./CONTRIBUTING.md).


[setup]: https://console.firebase.google.com/project/_/overview
[rules]: https://console.firebase.google.com/project/_/database/rules
[leadpages]: http://leadpages.net
[careers]: http://www.leadpages.net/careers
[contributors]: https://github.com/leadpages/gcloud_requests/graphs/contributors
