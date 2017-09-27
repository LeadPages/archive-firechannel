from firechannel import get_client


def test_can_get_default_client():
    # Given that I've got a testbed
    # If I try to get a client
    # I expect an instance to get created automatically
    assert get_client()
