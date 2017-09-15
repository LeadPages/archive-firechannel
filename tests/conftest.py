import os
import pytest
import time

from firechannel import Firebase, get_credentials, create_channel, delete_channel


@pytest.fixture(scope="session")
def credentials():
    key_file_path = os.getenv("SERVICE_KEY_FILE_PATH")
    assert key_file_path, "SERVICE_KEY_FILE_PATH must be set"
    return get_credentials(key_file_path)


@pytest.fixture(scope="session")
def client(credentials):
    project_name = os.getenv("FIREBASE_PROJECT")
    assert project_name, "FIREBASE_PROJECT must be set"
    return Firebase(project_name, credentials)


@pytest.fixture()
def random_channel(client):
    channel_id = "test-channel-" + str(int(time.time()))
    token = create_channel(channel_id, firebase_client=client)
    yield channel_id, token
    delete_channel(channel_id, firebase_client=client)
