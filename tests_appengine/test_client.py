from firechannel import get_client


def test_can_get_default_client():
    # Given that I've got a testbed
    # If I try to get a client
    # I expect an instance to get created automatically
    assert get_client()


def test_can_build_access_tokens():
    # Given that I've got a testbed and a client
    client = get_client()

    # That client must be able to generate an access token
    assert client.access_token


def test_can_refresh_access_tokens():
    # Given that I've got a testbed and a client
    client = get_client()

    # If I remove the auth token from Credentials
    client.credentials.token = None

    # I expect the underlying credentials to be refreshed
    assert client.access_token
