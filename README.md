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


## Testing

To run the tests, create a service account and point
`SERVICE_KEY_FILE_PATH` to it and `FIREBASE_PROJECT` to the name of
your project.  Finally, run `py.test`.


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
