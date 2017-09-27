import pytest
import os
import sys

appengine_path = os.getenv("APPENGINE_SDK_PATH")
assert appengine_path, "APPENGINE_SDK_PATH must be set"
sys.path.append(os.path.join(appengine_path, "python"))


from google.appengine.ext import testbed  # noqa


@pytest.fixture(autouse=True)
def appengine_testbed():
    tb = testbed.Testbed()
    tb.setup_env(app_id="unittest~firechannels")
    tb.activate()
    tb.init_app_identity_stub()
    yield tb
    tb.deactivate()
