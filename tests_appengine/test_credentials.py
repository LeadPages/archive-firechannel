from firechannel.credentials import build_token, decode_token


def test_can_build_and_decode_tokens(credentials):
    # Given that I've got a testbed and some GAE credentials

    # If I attempt to build a token
    params = {"uid": "hello"}
    token = build_token(credentials, params, 60)

    # Then decode it
    decoded_params = decode_token(credentials, token)

    # I expect the data I put in to still be there
    assert decoded_params["uid"] == "hello"
