from firechannel import get_credentials
from firechannel.credentials import build_token, decode_token
from google.auth.app_engine import Credentials


def test_can_build_appengine_credentials():
    # Given that I've got a testbed
    # If I try to get credentials, I expect to get back AppAssertionCredentials
    assert isinstance(get_credentials(), Credentials)


def test_can_build_and_decode_tokens():
    # Given that I've got a testbed and some credentials
    credentials = get_credentials()

    # If I attempt to build a token
    params = {"uid": "hello"}
    token = build_token(credentials, params, 60)

    # Then decode it
    decoded_params = decode_token(credentials, token)

    # I expect the data I put in to still be there
    assert decoded_params["uid"] == "hello"
