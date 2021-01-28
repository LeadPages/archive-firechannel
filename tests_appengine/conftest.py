import os
import sys

import pytest
from mock import patch

appengine_path = os.getenv("APPENGINE_SDK_PATH")
assert appengine_path, "APPENGINE_SDK_PATH must be set, i.e. google-cloud-sdk/platform/google_appengine"
sys.path.append(appengine_path)

# The 'google' package has modules we need in both the SDK path
# and the site-packages dir. Here we'll add the SDK path to the
# search paths so `google.appengine` can resolve.
import google  # noqa
sys.modules["google"].__path__.append(
    os.path.join(appengine_path, "google"),
)

from firechannel.credentials import SCOPES  # noqa
from google.appengine.ext import testbed  # noqa
import google.auth.app_engine  # noqa


@pytest.fixture(autouse=True)
def appengine_testbed():
    tb = testbed.Testbed()
    tb.setup_env(app_id="unittest~firechannels")
    tb.activate()
    tb.init_app_identity_stub()
    tb.init_memcache_stub()
    yield tb
    tb.deactivate()


@pytest.fixture
def credentials():
    return google.auth.app_engine.Credentials(scopes=SCOPES)


@pytest.fixture(autouse=True)
def mock_get_credentials(credentials):
    with patch("google.auth.default", ) as mock_get_credentials:
        mock_get_credentials.return_value = (credentials, "unittest-firechannel")
        yield mock_get_credentials
