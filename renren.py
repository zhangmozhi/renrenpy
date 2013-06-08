"""Python client SDK for Renren API using OAuth 2."""

#TODO: Add upload support.

__author__ = "Mozhi Zhang (zhangmozhi@gmail.com)"

import json
import time
import urllib
import urllib2
from StringIO import StringIO

class APIError(StandardError):
    """API exception class."""
    def __init__(self, code, message):
        self.code = code
        StandardError.__init__(self, message)

    def __str__(self):
        return "APIError: %s: %s" % (self.code, self.message)


def encode_params(**kw):
    """Return a URL-encoded string for a dictionary of paramteres."""
    return "&".join(["%s=%s" % (k, urllib.quote(str(v).encode("utf-8")))
                     for k, v in kw.iteritems()])


def decompress_gzip(compressed_str):
    """Decompress a string compressed by Gzip."""
    gzipper = gzip.GzipFile(fileobj=StringIO(compressed_str))
    decompressed_str = gzipper.read()
    gzipper.close()
    return decompressed_str


def http_post(url, **kw):
    """Send a HTTP Post request to the url and return a JSON object."""
    req = urllib2.Request(url, data=encode_params(**kw))
    req.add_header("Accept-Encoding", "gzip")
    resp = urllib2.urlopen(req)
    content = resp.read()
    if resp.headers.get("Content-Encoding", "") == "gzip":
        content = decompress_gzip(content)
    result = json.loads(content)
    if type(result) is not list and result.get("error_code"):
        raise APIError(result["error_code"], result["error_msg"])
    return result


class APIClient:
    """API client class."""
    #Oauth URI
    OAUTH_URI = "https://graph.renren.com/oauth/"

    #API Server URI
    API_SERVER = "https://api.renren.com/restserver.do"

    #API Version
    API_VERSION = "1.0"

    def __init__(self, app_key, app_secret, redirect_uri,
                 response_type="code"):
        self.app_key = str(app_key)
        self.app_secret = str(app_secret)
        self.redirect_uri = redirect_uri
        self.response_type = response_type
        self.access_token = None
        self.expires = 0.0

    def get_authorize_url(self, redirect_uri=None, scope=None,
                          force_relogin=False):
        """Return the authorization URL."""
        redirect = redirect_uri if redirect_uri else self.redirect_uri
        params = dict(client_id=self.app_key, redirect_uri=redirect,
                      response_type=self.response_type)
        if scope:
            params["scope"] = " ".join(scope)
        if force_relogin:
            params["x_renew"] = "true"
        return "%s%s?%s" % (APIClient.OAUTH_URI, "authorize", 
                            encode_params(**params))

    def request_access_token(self, code, redirect_uri=None):
        """Return the access token as a dict.
        The dict includes access_token, expires_in, refresh_token,
        and scope.
        """
        redirect = redirect_uri if redirect_uri else self.redirect_uri
        return http_post("%s%s" % (APIClient.OAUTH_URI, "token"),
                         grant_type="authorization_code", code=code,
                         client_id=self.app_key, redirect_uri=redirect,
                         client_secret=self.app_secret)

    def refresh_token(self, refresh_token):
        """Return the refreshed access token as a dict.
        The dict includes access_token, expires_in, refresh_token,
        and scope.
        """
        return http_post("%s%s" %(APIClient.OAUTH_URI, "token"),
                         grant_type="refresh_token", 
                         refresh_token=refresh_token,
                         client_id=self.app_key,
                         client_secret=self.app_secret)

    def set_access_token(self, access_token, expires):
        """Set access token for the API client."""
        self.access_token = str(access_token)
        self.expires = float(expires)

    def __getattr__(self, attr):
        return APIWrapper(self, attr)


class APIWrapper:
    """A wrapper for APIs."""
    def __init__(self, client, name):
        self.client = client
        self.name = name

    def __getattr__(self, attr):
        def request(**kw):
            """Send a HTTP Post request to the API server with specified 
            method.
            """
            params = dict(kw, access_token=self.client.access_token,
                          method="%s.%s" % (self.name, attr),
                          call_id=str(int(time.time() * 1000)),
                          v=APIClient.API_VERSION)
            params["format"] = "JSON"
            return http_post(APIClient.API_SERVER, **params)

        return request
