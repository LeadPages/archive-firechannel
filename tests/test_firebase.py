import pytest

from firechannel.errors import BadRequest
from mock import Mock, patch


@patch("requests.Session.request")
def test_firebase_client_retries_failed_access_tokens(request_mock, client):
    # Given that I have a firebase client
    # And I've mocked the Session.request to fail with a 401 error
    request_mock.return_value = Mock(status_code=401, text="Unauthorized request.")

    # If I make a request
    # I expect a BadRequest error to be raised
    with pytest.raises(BadRequest):
        client.get("firechannels.json")

    # And request to have been called 3 times
    assert len(request_mock.mock_calls) == 3
