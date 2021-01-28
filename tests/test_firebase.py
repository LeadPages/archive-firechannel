import pytest

from firechannel.errors import BadRequest
from mock import Mock, patch


@patch("requests.Session.request")
def test_firebase_client_retries_failed_access_tokens(request_mock, client):
    # Given that I have a firebase client
    # And I've mocked the Session.request to fail with a 401 error
    request_mock.return_value = Mock(
        status_code=401,
        content=b'{"error":"unauthorized_request"}',
        text='{"error":"unauthorized_request"}',
    )

    # If I make a request
    # I expect a BadRequest error to be raised
    with pytest.raises(BadRequest):
        client.get("firechannels.json")

    # And request to have been called 6 times
    request_count_by_method = [m.args[0] for m in request_mock.mock_calls]
    assert len(request_count_by_method) == 6
    # 3 times for each firebase request
    assert request_count_by_method.count("GET") == 3
    # And 3 times for the requests to refresh auth tokens.
    assert request_count_by_method.count("POST") == 3
