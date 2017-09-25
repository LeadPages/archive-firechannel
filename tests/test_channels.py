import json
import pytest

from base64 import urlsafe_b64decode
from firechannel import create_channel, delete_channel, send_message


def decode(blob):
    return json.loads(urlsafe_b64decode(blob))


def test_can_create_channels():
    try:
        # Given that I have a Firebase client
        # If I attempt to create a channel
        token = create_channel("test-channel")

        # I expect to get a valid token back
        header, payload, _ = token.split(".")
        header = decode(header)
        payload = decode(payload)

        assert header == {"alg": "RS256", "typ": "JWT"}
        assert payload["uid"] == "test-channel"

    finally:
        delete_channel("test-channel")


@pytest.mark.parametrize("value,error", [
    (50, TypeError),
    ("a" * 90, ValueError),
    ("foo/bar", ValueError),
    ("foo.json", ValueError),
])
def test_cant_create_channels_with_invalid_client_ids(value, error):
    # Given that I have a Firebase client
    # If I attempt to create a channel with an invalid id
    # I expect an error to be raised
    with pytest.raises(error):
        create_channel(value)


@pytest.mark.parametrize("value,error", [
    (90000, ValueError),
    ("foo", TypeError),
])
def test_cant_create_channels_with_invalid_expiration(value, error):
    # Given that I have a Firebase client
    # If I attempt to create a channel with an invalid duration
    # I expect an error to be raised
    with pytest.raises(error):
        create_channel("test-channel", duration_minutes=value)


def test_can_delete_channels(client, random_channel):
    # Given that I have a channel
    channel_id, _ = random_channel

    # If I attempt to delete it
    delete_channel(channel_id)

    # I expect it to be removed from Firebase
    assert client.get("firechannels/" + channel_id + ".json") is None


def test_can_send_messages_on_channels(client, random_channel):
    # Given that I have a channel
    channel_id, _ = random_channel

    # If I send it a message
    send_message(channel_id, "hello!")

    # I expect the channel to be updated in Firebase
    data = client.get("firechannels/" + channel_id + ".json")
    assert data["message"] == "hello!"
