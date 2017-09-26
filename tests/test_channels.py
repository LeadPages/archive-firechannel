import json
import pytest

from base64 import urlsafe_b64decode
from firechannel import create_channel, delete_channel, send_message
from firechannel.channel import decode_client_id


def decode(blob):
    return json.loads(urlsafe_b64decode(blob))


@pytest.mark.parametrize("client_id", (
    None,
    "test-channel",
))
def test_can_create_channels(client_id):
    try:
        # Given that I have a Firebase client
        # If I attempt to create a channel
        token = create_channel(client_id)

        # I expect to get a valid token back
        header, payload, _ = token.split(".")
        header = decode(header)
        payload = decode(payload)

        assert header == {"alg": "RS256", "typ": "JWT"}

        if client_id:
            assert payload["uid"] == "test-channel"
        else:
            assert payload["uid"]

    finally:
        if client_id:
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


def test_can_send_messages_on_channels_using_token(client, random_channel):
    # Given that I have a channel
    channel_id, token = random_channel

    # If I send it a message
    send_message(token, "hello!")

    # I expect the channel to be updated in Firebase
    data = client.get("firechannels/" + channel_id + ".json")
    assert data["message"] == "hello!"


def test_can_send_messages_on_anon_channels(credentials, client):
    try:
        # Given that I have an anonymous channel
        token = create_channel()
        channel_id = decode_client_id(token)

        # If I send it a message
        send_message(token, "hello!")

        # I expect the channel to be updated in Firebase
        data = client.get("firechannels/" + channel_id + ".json")
        assert data["message"] == "hello!"
    finally:
        delete_channel(channel_id)
