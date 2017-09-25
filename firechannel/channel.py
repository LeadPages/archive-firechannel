import string
import time

from .credentials import build_token
from .firebase import Firebase

_client = None

#: Valid client id characters.
VALID_CHARS = set(string.ascii_letters + string.digits + "-_")


def get_client():
    """Get the current global client instance.

    If one doesn't currently exist, a default client will be created
    and returned on GAE and a RuntimeError will be raised everywhere
    else.

    Returns:
      Firebase
    """
    global _client
    if _client is None:
        try:
            from google.appengine.api import app_identity
            _client = Firebase(app_identity.get_application_id())
        except ImportError:
            raise RuntimeError("Cannot use default client off of AppEngine.")

    return _client


def set_client(client):
    """Set the global client instance.

    Parameters:
      client(Firebase)
    """
    global _client
    _client = client


def _validate_client_id(client_id):
    if not isinstance(client_id, basestring):
        raise TypeError("client_id must be a string")

    elif len(client_id) > 64:
        raise ValueError("client_id must be at most 64 characters long")

    elif set(client_id) - VALID_CHARS:
        raise ValueError("client_id contains invalid characters")


def _validate_duration(duration_minutes):
    if not isinstance(duration_minutes, int):
        raise TypeError("duration_minutes must be an integer")

    elif not (1 <= duration_minutes <= 1440):
        raise ValueError("duration_minutes must be a value between 1 and 1440")


def create_channel(client_id, duration_minutes=60, firebase_client=None):
    """Create a channel.

    Parameters:
      client_id(str): A string to identify this channel in Firebase.
      duration_minutes(int): An int specifying the number of minutes
        for which the returned should be valid.
      firebase_client(Firebase): The Firebase client instance to
        use. This can be omitted on AppEngine.

    Raises:
      FirebaseError: When Firebase is down.
      TypeError: When client_id or duration_minutes have invalid types.
      ValueError: When client_id or duration_minutes have invalid values.

    Returns:
      str: A token that the client can use to connect to the channel.
    """
    _validate_client_id(client_id)
    _validate_duration(duration_minutes)

    client = firebase_client or get_client()
    params = {"uid": client_id}

    # Delete the channel so any old data isn't sent to the client.
    delete_channel(client_id, firebase_client=client)

    return build_token(client.credentials, params, duration_minutes)


def delete_channel(client_id, firebase_client=None):
    """Delete a channel.

    Parameters:
      client_id(str): A string to identify this channel in Firebase.
      firebase_client(Firebase): The Firebase client instance to
        use. This can be omitted on AppEngine.

    Raises:
      FirebaseError: When Firebase is down.
      TypeError: When client_id has an invalid type.
      ValueError: When client_id has an invalid value.
    """
    _validate_client_id(client_id)
    client = firebase_client or get_client()
    client.delete(u"firechannels/{}.json".format(client_id))


def send_message(client_id, message, firebase_client=None):
    """Send a message to a channel.

    Parameters:
      client_id(str): A string to identify this channel in Firebase.
      message(str): A string representing the message to send.
      firebase_client(Firebase): The Firebase client instance to
        use. This can be omitted on AppEngine.

    Raises:
      FirebaseError: When Firebase is down.
      TypeError: When client_id has an invalid type.
      ValueError: When client_id has an invalid value.
    """
    _validate_client_id(client_id)
    client = firebase_client or get_client()
    client.patch(u"firechannels/{}.json".format(client_id), {
        "message": message,
        "timestamp": int(time.time() * 1000),
    })
