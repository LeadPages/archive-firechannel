import hmac
import json
import time

from base64 import urlsafe_b64encode, urlsafe_b64decode

try:
    from google.appengine.api import app_identity
    from oauth2client.appengine import AppAssertionCredentials

    ON_APPENGINE = True
except ImportError:
    from oauth2client.client import GoogleCredentials

    ON_APPENGINE = False


def encode(data):
    return urlsafe_b64encode(json.dumps(data, separators=(",", ":")))


def decode(data):
    return json.loads(urlsafe_b64decode(data))


#: The OAuth2 scopes to request when authenticating with Google.
SCOPES = [
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/firebase.database"
]

#: The endpoint used to verify identities.
IDENTITY_ENDPOINT = "https://identitytoolkit.googleapis.com/"


#: The standard token header.
TOKEN_HEADER = encode({"typ": "JWT", "alg": "RS256"})


def get_appengine_credentials():
    """Generates a credentials object for the current environment.

    Returns:
      GoogleCredentials
    """
    return AppAssertionCredentials.create_scoped(SCOPES)


def get_service_key_credentials(key_file_path):
    """Generate a credentials object from a service key.

    Parameters:
      key_file_path(str): The absolute path to a service key file.

    Returns:
      GoogleCredentials
    """
    credentials = GoogleCredentials.from_stream(key_file_path)
    credentials._scopes = " ".join(SCOPES)
    return credentials


def _build_token(credentials, issuer, params, duration_minutes):
    issued_at = int(time.time())

    data = {
        "iss": issuer,
        "sub": issuer,
        "aud": IDENTITY_ENDPOINT,
        "iat": issued_at,
        "exp": issued_at + duration_minutes * 60,
    }
    data.update(params)

    payload = TOKEN_HEADER + "." + encode(data)
    _, signature = credentials.sign_blob(payload)
    return payload + "." + urlsafe_b64encode(signature)


def build_token_appengine(_, params, duration_minutes):
    """Build a token on AppEngine.
    """
    issuer = app_identity.get_service_account_name()
    return _build_token(app_identity, issuer, params, duration_minutes)


def build_token_service_key(credentials, params, duration_minutes):
    """Build a token using a service key.
    """
    issuer = credentials._service_account_email
    return _build_token(credentials, issuer, params, duration_minutes)


def _decode_token(credentials, token, verify):
    try:
        header, data, signature = token.split(".")
    except ValueError:
        raise ValueError("Invalid token data.")

    if header != TOKEN_HEADER:
        raise ValueError("Invalid token header.")

    if verify:
        payload = header + "." + data
        given_signature = urlsafe_b64decode(signature)
        _, expected_signature = credentials.sign_blob(payload)
        if not hmac.compare_digest(given_signature, expected_signature):
            raise ValueError("Invalid token signature.")

    return decode(data)


def decode_token_appengine(_, token, verify=True):
    """Decode a token on AppEngine.
    """
    return _decode_token(app_identity, token, verify)


def decode_token_service_key(credentials, token, verify=True):
    """Decode a token on AppEngine.
    """
    return _decode_token(credentials, token, verify)


if ON_APPENGINE:
    get_credentials = get_appengine_credentials
    build_token = build_token_appengine
    decode_token = decode_token_appengine
else:
    get_credentials = get_service_key_credentials
    build_token = build_token_service_key
    decode_token = decode_token_service_key
