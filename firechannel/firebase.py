import logging
import requests

from functools import partial
from threading import Lock

from google.auth.transport.requests import Request
from google.auth.exceptions import GoogleAuthError

from .credentials import ON_APPENGINE, get_credentials
from .errors import BadRequest, ConnectionError, NotFound, ServerError, Timeout
from .pool import ThreadLocalPool

_logger = logging.getLogger("firechannel.firebase")

#: The max number of times Authorization errors are attempted.
MAX_AUTH_ATTEMPTS = 3


class Firebase(object):
    """A simple firebase real time database client.

    Parameters:
      project(str): The name of the project.
      credentials(Credentials): An OAuth2 credentials object.
        Optional on Google App Engine.
      timeout(tuple): Connect and read timeout.
    """

    URI_TEMPLATE = u"https://{project}.firebaseio.com/{path}"

    def __init__(self, project, credentials=None, timeout=(3.05, 15), pool_factory=ThreadLocalPool):
        if not credentials:
            if not ON_APPENGINE:
                raise ValueError(
                    "You must provide a valid set of credentials. "
                    "See Credentials.get_credentials() for details."
                )

            credentials = get_credentials()

        self.credentials = credentials
        self.project = project
        self.timeout = timeout
        self.pool = pool_factory(requests.Session)

        self._access_token_mutex = Lock()

    def __auth(self, request):
        access_token = self.access_token
        _logger.debug("Using access token %r.", access_token)
        request.headers["Authorization"] = "Bearer " + access_token
        return request

    def __build_uri(self, path):
        return Firebase.URI_TEMPLATE.format(
            project=self.project,
            path=path.lstrip("/"),
        )

    def refresh_token(self):
        with self._access_token_mutex:
            self.credentials.refresh(Request())

    @property
    def access_token(self):
        if not self.credentials.valid:
            self.refresh_token()
        return self.credentials.token

    def call(self, method, path, value=None):
        """Call the Firebase API.

        Parameters:
          method(str): HTTP method.
          path(str): Request path.
          value(dict): The value to send to Firebase.
        """
        with self.pool.reserve() as session:
            call = getattr(session, method.lower())
            endpoint = self.__build_uri(path)
            attempts = 1

            try:
                while attempts <= MAX_AUTH_ATTEMPTS:
                    response = call(endpoint, json=value, auth=self.__auth, timeout=self.timeout)
                    if response.status_code != 401:
                        break

                    _logger.debug("Access token failed. Retrying. [%d/%d]", attempts, MAX_AUTH_ATTEMPTS)
                    try:
                        self.refresh_token()
                    except GoogleAuthError, e:
                        _logger.warning("Failed refreshing access token: %s", e)
                    attempts += 1

                if response.status_code >= 500:
                    raise ServerError(response.text, cause=response)
                elif response.status_code == 404:
                    raise NotFound(response.text, cause=response)
                elif response.status_code >= 400:
                    raise BadRequest(response.text, cause=response)

                return response.json()

            except requests.exceptions.Timeout as e:
                raise Timeout("timeout", cause=e)

            except requests.exceptions.ConnectionError as e:
                raise ConnectionError("connection error", cause=e)

    def __getattr__(self, name):
        if name in ("delete", "head", "get", "patch", "post", "put"):
            return partial(self.call, name)
        raise AttributeError("Firebase object has no attribute {!r}".format(name))
