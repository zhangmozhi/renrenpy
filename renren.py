"""Python SDK for Renren API using OAuth 2 authentication."""

__author__ = "Mozhi Zhang (zhangmozhi@gmail.com)"

import json
import time
import urllib
import urllib2


#HTTP Method code
GET = 0
POST = 1
UPLOAD = 2

#Keyword for GET method
GET_KEYWORDS = ["get", "list", "batch"]


class APIError(StandardError):
    """API exception class."""
    def __init__(self, code, message):
        self.code = code
        StandardError.__init__(self, message)

    def __unicode__(self):
        return u"APIError: %s: %s" % (self.code, self.message)

    def __str__(self):
        return unicode(self).encode("utf-8")


def encode_str(obj):
    """Encode an object into a utf-8 string."""
    if isinstance(obj, basestring):
        return obj.encode("utf-8") if isinstance(obj, unicode) else obj
    return str(obj)


def encode_params(**kw):
    """Return a URL-encoded string for a dictionary of paramteres."""
    return "&".join(["%s=%s" % (k, urllib.quote(encode_str(v)))
                     for k, v in kw.iteritems()])


def guess_content_type(name):
    """Return the content type by the extension of the filename."""
    if name.endswith(".jpg"):
        return "image/jpg"
    elif name.endswith(".jpeg"):
        return "image/jpeg"
    elif name.endswith(".png"):
        return "image/png"
    elif name.endswith(".gif"):
        return "image/gif"
    elif name.endswith(".bmp"):
        return "image.bmp"
    return "image/jpg"


def encode_multipart(**kw):
    """Return a multipart/form-data body with a randomly generated boundary.
    """
    boundary = "----------%s" % hex(int(time.time() * 1000))
    params = []
    for k, v in kw.iteritems():
        params.append("--%s" % boundary)
        if hasattr(v, "read") and hasattr(v, "name"):
            content = v.read()
            filename = v.name
            params.append("Content-Disposition: form-data; name=\"%s\";"
                          "filename=\"%s\"" % (k, filename))
            params.append("Content-Type: %s\r\n" %
                          guess_content_type(filename))
            params.append(content)
        else:
            params.append("Content-Disposition: form-data; name=\"%s\"\r\n"
                          % k)
            params.append(encode_str(v))
    params.append("--%s--\r\n" % boundary)
    return "\r\n".join(params), boundary


def http_call(url, http_method=POST, **kw):
    """Send a HTTP request to the url and return a JSON object."""
    params = None
    boundary = None
    if http_method == UPLOAD:
        params, boundary = encode_multipart(**kw)
    else:
        params = encode_params(**kw)

    req = None
    if http_method == GET:
        req = urllib2.Request("%s?%s" % (url, params))
    else:
        req = urllib2.Request(url, data=params)
    if http_method == UPLOAD:
        req.add_header("Content-Type",
                       "multipart/form-data; boundary=%s" % boundary)

    try:
        resp = urllib2.urlopen(req)
        content = resp.read()
        result = json.loads(content)
        if type(result) is not list and result.get("error_code"):
            raise APIError(result.get("error_code", ""),
                           result.get("error_msg", ""))
        return result
    except urllib2.HTTPError as e:
        raise e


class APIClient:
    """API client class."""
    #Oauth URI
    OAUTH_URI = "https://graph.renren.com/oauth/"

    def __init__(self, app_key, app_secret, redirect_uri,
                 response_type="code", version=2):
        self.app_key = str(app_key)
        self.app_secret = str(app_secret)
        self.redirect_uri = redirect_uri
        self.response_type = response_type
        self.access_token = None
        self.version = version

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
        return http_call("%s%s" % (APIClient.OAUTH_URI, "token"), POST,
                         grant_type="authorization_code", code=code,
                         client_id=self.app_key, redirect_uri=redirect,
                         client_secret=self.app_secret)

    def refresh_token(self, refresh_token):
        """Return the refreshed access token as a dict.
        The dict includes access_token, expires_in, refresh_token,
        and scope.
        """
        return http_call("%s%s" % (APIClient.OAUTH_URI, "token"), POST,
                         grant_type="refresh_token",
                         refresh_token=refresh_token,
                         client_id=self.app_key,
                         client_secret=self.app_secret)

    def set_access_token(self, access_token):
        """Set access token for the API client."""
        self.access_token = str(access_token)

    def __getattr__(self, attr):
        if self.version == 2:
            return APIWrapperV2(self, attr)
        return APIWrapper(self, attr)


class APIWrapper:
    """Wrapper Class for API 1.0."""
    #API Server URI
    API_SERVER = "https://api.renren.com/restserver.do"

    #API Version
    API_VERSION = "1.0"

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
                          v=APIWrapper.API_VERSION)
            if not params.get("format"):
                params["format"] = "JSON"
            http_method = UPLOAD if attr == "upload" else POST
            return http_call(APIWrapper.API_SERVER, http_method, **params)

        return request


class APIWrapperV2():
    """Wrapper class for API 2.0."""
    #API Server URI
    API_SERVER = "https://api.renren.com/v2"

    def __init__(self, client, name):
        self.client = client
        self.name = name

    def __getattr__(self, attr):
        return APIWrapperV2(self.client, "%s/%s" % (self.name, attr))

    def __call__(self, **kw):
        """Send a HTTP Post request to the API server with specified
        method.
        """
        params = dict(kw, access_token=self.client.access_token)
        http_method = POST
        if any(w in self.name for w in GET_KEYWORDS):
            http_method = GET
        elif "upload" in self.name:
            http_method = UPLOAD
        return http_call("%s/%s" % (APIWrapperV2.API_SERVER, self.name),
                         http_method, **params)
