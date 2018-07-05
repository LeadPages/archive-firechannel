import json
import pytest

from base64 import b64decode
from firechannel import create_channel, delete_channel, send_message, find_all_expired_channels
from firechannel.channel import decode_client_id


def decode(blob):
    return json.loads(b64decode(blob))


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
    assert b64decode(data["message"]) == "hello!"


def test_can_send_messages_on_channels_using_token(client, random_channel):
    # Given that I have a channel
    channel_id, token = random_channel

    # If I send it a message
    send_message(token, "hello!")

    # I expect the channel to be updated in Firebase
    data = client.get("firechannels/" + channel_id + ".json")
    assert b64decode(data["message"]) == "hello!"


def test_can_send_messages_on_anon_channels(credentials, client):
    try:
        # Given that I have an anonymous channel
        token = create_channel()
        channel_id = decode_client_id(token)

        # If I send it a message
        send_message(token, "hello!")

        # I expect the channel to be updated in Firebase
        data = client.get("firechannels/" + channel_id + ".json")
        assert b64decode(data["message"]) == "hello!"
    finally:
        delete_channel(channel_id)


def test_can_clean_up_old_channels(client):
    # Given that I have a few channels
    channel_ids = []
    for _ in range(10):
        token = create_channel()
        channel_ids.append(decode_client_id(token))

        # If I send each of those a message
        send_message(token, "hello!")

    # Then delete all expired channels
    expired_channels = find_all_expired_channels(max_age=0)
    for channel_id in expired_channels:
        delete_channel(channel_id)

    # I expect all of them to have been deleted
    channels = client.get("firechannels.json") or {}
    for channel_id in channel_ids:
        assert channel_id not in channels


def test_can_clean_up_broken_channels(client):
    # Given that I have a few channels
    channel_ids = []
    for _ in range(10):
        token = create_channel()
        channel_ids.append(decode_client_id(token))

        # And I've sent each of those a message
        send_message(token, "hello!")

    # And somehow a message was written directly to firechannels.json
    client.patch(u"firechannels.json".format(client_id), {
        "message": "AM BROKEN!",
        "timestamp": 500,
    })

    # Then when I delete all expired channels
    expired_channels = find_all_expired_channels(max_age=0)
    for channel_id in expired_channels:
        delete_channel(channel_id)

    # I expect all of them to have been deleted
    channels = client.get("firechannels.json") or {}
    for channel_id in channel_ids:
        assert channel_id not in channels

    # Including the broken ones
    assert "message" not in channels
    assert "timestamp" not in channels


def test_find_all_expired_channels_can_return_no_results(client):
    # Given that I have no channels older than 365 days
    # If I try to find all channels that have last received a message longer than 365 days ago
    expired_channels = find_all_expired_channels(max_age=86400 * 365)

    # I expect to get back an empty generator
    assert not list(expired_channels)
