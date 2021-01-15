import hmac
import json
import time

from google.oauth2 import service_account
from google.auth import app_engine

from base64 import b64encode, b64decode


try:
    from google.appengine.api import app_identity

    ON_APPENGINE = True
except ImportError:
    ON_APPENGINE = False


def encode(data):
    return b64encode(json.dumps(data, separators=(",", ":")))


def decode(data):
    return json.loads(b64decode(data))


#: The OAuth2 scopes to request when authenticating with Google.
SCOPES = [
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/firebase.database"
]

#: The endpoint used to verify identities.
IDENTITY_ENDPOINT = "https://identitytoolkit.googleapis.com/google.identity.identitytoolkit.v1.IdentityToolkit"


#: The standard token header.
TOKEN_HEADER = encode({"typ": "JWT", "alg": "RS256"})


def get_appengine_credentials():
    """Generates a credentials object for the current environment.

    Returns:
      google.auth.app_engine.Credentials
    """
    return app_engine.Credentials(scopes=SCOPES)


def get_service_key_credentials(key_file_path):
    """Generate a credentials object from a service key.

    Parameters:
      key_file_path(str): The absolute path to a service key file.

    Returns:
      google.oauth2.service_account.Credentials
    """
    credentials = service_account.Credentials.from_service_account_file(
        key_file_path,
        scopes=SCOPES,
    )
    return credentials


def build_token(credentials, params, duration_minutes):
    issuer = credentials.service_account_email
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
    signature = credentials.sign_bytes(payload)
    return payload + "." + b64encode(signature)


def _decode_token(credentials, token, verify):
    try:
        header, data, signature = map(str, token.split("."))
    except ValueError:
        raise ValueError("Invalid token data.")

    if header != TOKEN_HEADER:
        raise ValueError("Invalid token header.")

    if verify:
        payload = header + "." + data
        given_signature = b64decode(signature)
        expected_signature = credentials.sign_bytes(payload)
        if not hmac.compare_digest(given_signature, expected_signature):
            raise ValueError("Invalid token signature.")

    return decode(data)


def decode_token_appengine(credentials, token, verify=False):
    """Decode a token on AppEngine.

    Warning:
      Token verification is disabled on GAE.
    """
    return _decode_token(credentials, token, False)


def decode_token_service_key(credentials, token, verify=True):
    """Decode a token from a service account.
    """
    return _decode_token(credentials, token, verify)


if ON_APPENGINE:
    get_credentials = get_appengine_credentials
    decode_token = decode_token_appengine
else:
    get_credentials = get_service_key_credentials
    decode_token = decode_token_service_key
